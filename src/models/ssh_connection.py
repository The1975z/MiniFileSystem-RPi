import paramiko
import os
from typing import Optional, Tuple, Callable
from pathlib import Path
import time
import posixpath


def _clean_remote_path(p: Optional[str]) -> str:
    """
    ทำความสะอาดพาธฝั่งรีโมตให้เป็น POSIX absolute เสมอ
    - ตัดช่องว่าง/quote
    - แทน backslash -> slash
    - บีบ '//' และลบ ./ ../
    - บังคับขึ้นต้นด้วย '/'
    """
    if not p:
        return "/"
    p = p.strip().strip('"').strip("'").replace("\\", "/")
    p = posixpath.normpath(p)
    if not p.startswith("/"):
        p = "/" + p
    return p


class SSHConnection:
    def __init__(self):
        self.client: Optional[paramiko.SSHClient] = None
        self.sftp: Optional[paramiko.SFTPClient] = None
        self.connected = False
        self.current_path = "/"
        self.on_progress: Optional[Callable[[str], None]] = None

    def connect(
        self,
        host: str,
        port: int,
        username: str,
        password: Optional[str] = None,
        identity_file: Optional[str] = None,
        passphrase: Optional[str] = None
    ) -> Tuple[bool, str]:
        try:
            from utils.logger import logger

            logger.log_connection_attempt(host, port, username, "SSH")
            self._report_progress("searching_host")

            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            time.sleep(0.5)
            self._report_progress("connecting")
            time.sleep(0.5)
            self._report_progress("authenticating")
            time.sleep(0.3)
            self._report_progress("using_username")

            if identity_file and os.path.exists(identity_file):
                self._report_progress("loading_keys")
                logger.info(f"Loading SSH key from: {identity_file}", "SSHConnection.connect")

                if identity_file.endswith('.pub'):
                    error_msg = (
                        "ไฟล์ที่เลือกเป็น Public Key (.pub)\n"
                        "กรุณาเลือก Private Key (id_rsa หรือ id_ed25519)\n\n"
                        "You selected a Public Key (.pub)\n"
                        "Please select Private Key (id_rsa or id_ed25519)"
                    )
                    logger.error("User selected .pub file instead of private key", "SSHConnection.connect")
                    return False, error_msg

                try:
                    key = self._load_private_key(identity_file, passphrase)
                    if key is None:
                        suggestion = self._suggest_correct_key(identity_file)
                        error_msg = f"ไม่สามารถโหลด Private Key ได้\n\n{suggestion}"
                        return False, error_msg

                    key_comment = getattr(key, 'comment', 'default')
                    self._report_progress("auth_public_key", key=key_comment)
                    logger.info(f"Using public key: {key_comment}", "SSHConnection.connect")

                    time.sleep(0.8)
                    self.client.connect(
                        hostname=host,
                        port=port,
                        username=username,
                        pkey=key,
                        timeout=15
                    )
                except paramiko.ssh_exception.SSHException as e:
                    if "private key file is encrypted" in str(e).lower() or "passphrase" in str(e).lower():
                        logger.warning("SSH key requires passphrase", "SSHConnection.connect")
                        return False, "PASSPHRASE_REQUIRED"
                    raise

            elif password:
                self._report_progress("auth_password")
                logger.info("Using password authentication", "SSHConnection.connect")
                time.sleep(0.8)
                self.client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    password=password,
                    timeout=15
                )
            else:
                logger.error("No authentication method provided", "SSHConnection.connect")
                return False, "No authentication method provided"

            time.sleep(0.5)
            self.sftp = self.client.open_sftp()
            self.connected = True

            # บาง server คืน None เมื่ออยู่ root → บังคับ normalize
            cwd = self.sftp.getcwd()
            self.current_path = _clean_remote_path(cwd)

            self._report_progress("success")
            logger.log_connection_success(host)
            return True, "Connected successfully"

        except paramiko.AuthenticationException:
            from utils.logger import logger
            error_msg = "Authentication failed"
            logger.log_connection_failure(host, error_msg)
            self._report_progress("failed")
            return False, error_msg

        except paramiko.SSHException as e:
            from utils.logger import logger
            error_msg = f"SSH error: {str(e)}"
            logger.log_connection_failure(host, error_msg)
            self._report_progress("failed")
            return False, error_msg

        except Exception as e:
            from utils.logger import logger
            error_msg = f"Connection error: {str(e)}"
            logger.exception("Unexpected connection error", "SSHConnection.connect")
            self._report_progress("failed")
            return False, error_msg

    def _suggest_correct_key(self, key_path: str) -> str:
        suggestions = []
        key_dir = os.path.dirname(key_path)
        key_name = os.path.basename(key_path)

        if key_path.endswith('.ppk'):
            suggestions.append("❌ ไฟล์ .ppk เป็นรูปแบบของ PuTTY")
            suggestions.append("✓ กรุณาใช้ไฟล์ id_rsa (ไม่มีนามสกุล) แทน")
            openssh_key = os.path.join(key_dir, key_name.replace('.ppk', ''))
            if os.path.exists(openssh_key):
                suggestions.append(f"✓ พบไฟล์: {openssh_key}")
        elif key_path.endswith('.pub'):
            suggestions.append("❌ ไฟล์ .pub เป็น Public Key")
            suggestions.append("✓ กรุณาใช้ไฟล์ Private Key (id_rsa) แทน")
            private_key = key_path.replace('.pub', '')
            if os.path.exists(private_key):
                suggestions.append(f"✓ พบไฟล์: {private_key}")
        else:
            suggestions.append("ไม่สามารถโหลดไฟล์นี้ได้")
            suggestions.append("รูปแบบที่รองรับ: RSA, ED25519, ECDSA")
            suggestions.append("กรุณาตรวจสอบว่าไฟล์ถูกต้อง")

        return "\n".join(suggestions)

    def _load_private_key(self, key_path: str, passphrase: Optional[str] = None):
        from utils.logger import logger

        if key_path.endswith('.ppk'):
            logger.warning("PuTTY format (.ppk) detected, trying conversion", "SSHConnection._load_private_key")
            try:
                return self._load_putty_key(key_path, passphrase)
            except Exception as e:
                logger.error(f"Failed to load PuTTY key: {str(e)}", "SSHConnection._load_private_key")
                return None

        key_loaders = [
            (paramiko.RSAKey, "RSA"),
            (paramiko.Ed25519Key, "ED25519"),
            (paramiko.ECDSAKey, "ECDSA"),
        ]

        if hasattr(paramiko, 'DSSKey'):
            key_loaders.append((paramiko.DSSKey, "DSS"))

        for key_class, key_type in key_loaders:
            try:
                if passphrase:
                    key = key_class.from_private_key_file(key_path, password=passphrase)
                else:
                    key = key_class.from_private_key_file(key_path)
                logger.info(f"Successfully loaded {key_type} key", "SSHConnection._load_private_key")
                return key
            except paramiko.ssh_exception.SSHException as e:
                if "private key file is encrypted" in str(e).lower() or "passphrase" in str(e).lower():
                    raise
                continue
            except Exception:
                continue

        logger.error(f"Failed to load key from {key_path} with any supported format", "SSHConnection._load_private_key")
        return None

    def _load_putty_key(self, key_path: str, passphrase: Optional[str] = None):
        from utils.logger import logger
        import io

        try:
            with open(key_path, 'r') as f:
                key_data = f.read()

            key_obj = paramiko.RSAKey.from_private_key(io.StringIO(key_data), password=passphrase)
            logger.info("Successfully converted PuTTY key", "SSHConnection._load_putty_key")
            return key_obj
        except Exception as e:
            logger.error(f"PuTTY key conversion failed: {str(e)}", "SSHConnection._load_putty_key")

            openssh_path = key_path.replace('.ppk', '')
            if os.path.exists(openssh_path):
                logger.info(f"Trying OpenSSH format at: {openssh_path}", "SSHConnection._load_putty_key")
                return self._load_private_key(openssh_path, passphrase)

            raise Exception("Cannot load PuTTY key. Please use OpenSSH format (id_rsa without extension)")

    def _report_progress(self, status: str, **kwargs):
        if self.on_progress:
            self.on_progress(status, **kwargs)

    def disconnect(self):
        if self.sftp:
            self.sftp.close()
        if self.client:
            self.client.close()
        self.connected = False
        self.current_path = "/"

    def is_connected(self) -> bool:
        return self.connected and self.client is not None

    def execute_command(self, command: str) -> Tuple[str, str, int]:
        from utils.logger import logger

        if not self.is_connected():
            logger.warning("Command execution attempted while not connected", "SSHConnection.execute_command")
            return "", "Not connected", 1

        try:
            logger.debug(f"Executing command: {command}", "SSHConnection.execute_command")
            stdin, stdout, stderr = self.client.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            stdout_text = stdout.read().decode()
            stderr_text = stderr.read().decode()

            logger.log_ssh_command(command, exit_code)
            if stderr_text:
                logger.warning(f"Command stderr: {stderr_text[:200]}", "SSHConnection.execute_command")

            return stdout_text, stderr_text, exit_code
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}", "SSHConnection.execute_command")
            return "", str(e), 1

    def get_sftp(self) -> Optional[paramiko.SFTPClient]:
        return self.sftp if self.is_connected() else None

    def change_directory(self, path: str):
        """
        Robust chdir:
        - ทำความสะอาดพาธให้เป็น POSIX absolute
        - ลอง chdir(target) → ถ้าพังลอง normalize(target) แล้ว chdir อีกครั้ง
        - อัปเดต self.current_path แบบ normalize เสมอ
        - log เป้าหมายตอน fail เพื่อดีบัก Errno 2 ได้ง่าย
        """
        if not self.sftp:
            raise RuntimeError("SFTP not connected")

        from utils.logger import logger  # import ภายในเพื่อเลี่ยงปัญหาวงจรอิมพอร์ต

        target = _clean_remote_path(path)
        try:
            self.sftp.chdir(target)
        except Exception as e1:
            try:
                canonical = self.sftp.normalize(target)
                self.sftp.chdir(canonical)
                target = canonical
            except Exception as e2:
                try:
                    cwd_before = self.sftp.getcwd()
                except Exception:
                    cwd_before = None
                logger.error(
                    f"[SFTP] chdir failed. target={repr(target)} cwd_before={repr(cwd_before)} e1={e1} e2={e2}",
                    "SSHConnection.change_directory"
                )
                raise

        cwd = self.sftp.getcwd() or target
        self.current_path = _clean_remote_path(cwd)

    def get_current_path(self) -> str:
        return self.current_path or "/"
