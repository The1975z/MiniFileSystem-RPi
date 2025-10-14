import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Optional
import os
import time
from views.sidebar import Sidebar
from views.file_browser import FileBrowser
from views.local_browser import LocalBrowser
from views.terminal_view import TerminalView
from views.connection_dialog import ConnectionDialog
from views.passphrase_dialog import PassphraseDialog
from controllers.main_controller import MainController
class MainView(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FILE-MANAGEMENT-SYSTEM-OS")
        self.geometry("1400x800")

        self.controller = MainController()
        self.selected_local_file = None
        self.selected_remote_file = None
        self.connection_start_time = None
        self.connection_timer_running = False
        self.disk_usage_retry_count = 0

        self._setup_ui()
        self._bind_controllers()

    def _setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        main_container = ctk.CTkFrame(self)
        main_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)

        toolbar_frame = ctk.CTkFrame(main_container, height=50)
        toolbar_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        toolbar_frame.grid_columnconfigure(1, weight=1)

        self.back_btn = ctk.CTkButton(
            toolbar_frame,
            text="←",
            width=40,
            command=self._handle_back,
            state="disabled"
        )
        self.back_btn.grid(row=0, column=0, padx=5)

        self.forward_btn = ctk.CTkButton(
            toolbar_frame,
            text="→",
            width=40,
            command=self._handle_forward,
            state="disabled"
        )
        self.forward_btn.grid(row=0, column=1, padx=5)

        self.up_btn = ctk.CTkButton(
            toolbar_frame,
            text="↑",
            width=40,
            command=self._handle_up,
            state="disabled"
        )
        self.up_btn.grid(row=0, column=2, padx=5)

        self.path_entry = ctk.CTkEntry(
            toolbar_frame,
            placeholder_text="เส้นทางปัจจุบัน"
        )
        self.path_entry.grid(row=0, column=3, padx=10, sticky="ew")
        self.path_entry.bind("<Return>", self._handle_path_enter)

        self.search_entry = ctk.CTkEntry(
            toolbar_frame,
            placeholder_text="ค้นหา...",
            width=200
        )
        self.search_entry.grid(row=0, column=4, padx=5)
        self.search_entry.bind("<KeyRelease>", self._handle_search)

        self.tabview = ctk.CTkTabview(main_container)
        self.tabview.grid(row=1, column=0, sticky="nsew")

        self.tabview.add("📂 ไฟล์")
        self.tabview.add("💻 Terminal")

        self._setup_file_tab()
        self._setup_terminal_tab()

        status_frame = ctk.CTkFrame(main_container, height=30)
        status_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="ไม่ได้เชื่อมต่อ",
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5)

        self.connection_timer_label = ctk.CTkLabel(
            status_frame,
            text="",
            anchor="center"
        )
        self.connection_timer_label.pack(side="left", padx=20, pady=5)

        self.disk_usage_label = ctk.CTkLabel(
            status_frame,
            text="",
            anchor="e"
        )
        self.disk_usage_label.pack(side="right", padx=10, pady=5)

    def _setup_file_tab(self):
        file_tab = self.tabview.tab("📂 ไฟล์")
        file_tab.grid_columnconfigure(0, weight=1)
        file_tab.grid_columnconfigure(1, weight=1)
        file_tab.grid_rowconfigure(0, weight=1)

        self.local_browser = LocalBrowser(file_tab)
        self.local_browser.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        self.remote_browser = FileBrowser(file_tab, title="🌐 เซิร์ฟเวอร์ (Remote)")
        self.remote_browser.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        transfer_frame = ctk.CTkFrame(file_tab, width=60)
        transfer_frame.grid(row=0, column=2, padx=(10, 0), sticky="ns")

        ctk.CTkLabel(
            transfer_frame,
            text="คัดลอก",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(20, 10))

        self.upload_btn = ctk.CTkButton(
            transfer_frame,
            text="→\nอัปโหลด",
            width=60,
            height=60,
            command=self._quick_upload,
            state="disabled"
        )
        self.upload_btn.pack(pady=10)

        self.download_btn = ctk.CTkButton(
            transfer_frame,
            text="←\nดาวน์โหลด",
            width=60,
            height=60,
            command=self._quick_download,
            state="disabled"
        )
        self.download_btn.pack(pady=10)

    def _setup_terminal_tab(self):
        terminal_tab = self.tabview.tab("💻 Terminal")
        terminal_tab.grid_columnconfigure(0, weight=1)
        terminal_tab.grid_rowconfigure(0, weight=1)

        self.terminal = TerminalView(terminal_tab)
        self.terminal.grid(row=0, column=0, sticky="nsew")
        self.terminal.on_command = self._handle_terminal_command

    def _bind_controllers(self):
        self.sidebar.on_connect = self._handle_connect
        self.sidebar.on_load_config = self._handle_load_config
        self.sidebar.on_disconnect = self._handle_disconnect
        self.sidebar.on_refresh = self._handle_refresh
        self.sidebar.on_upload = self._handle_upload
        self.sidebar.on_new_file = self._handle_new_file
        self.sidebar.on_new_folder = self._handle_new_folder
        self.sidebar.on_appearance_change = self._handle_appearance_change
        self.sidebar.on_language_change = self._handle_language_change

        self.remote_browser.on_file_select = self._handle_remote_file_select
        self.remote_browser.on_file_double_click = self._handle_remote_file_double_click
        self.remote_browser.on_context_menu = self._handle_context_menu

        self.local_browser.on_file_select = self._handle_local_file_select

        file_controller = self.controller.get_file_controller()
        file_controller.on_directory_change = self._on_directory_changed

    def _handle_connect(self):
        conn_controller = self.controller.get_connection_controller()
        saved_connections = conn_controller.get_saved_connections()

        dialog = ConnectionDialog(self, saved_connections)
        dialog.on_save = lambda name: conn_controller.load_connection_config(name)
        dialog.on_connect = self._process_connection
        self.wait_window(dialog)

    def _handle_load_config(self):
        conn_controller = self.controller.get_connection_controller()
        saved_connections = conn_controller.get_saved_connections()

        if not saved_connections:
            messagebox.showinfo("ข้อมูล", "ไม่มีการเชื่อมต่อที่บันทึกไว้")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("โหลดการเชื่อมต่อ")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.grab_set()

        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main_frame,
            text="เลือกการเชื่อมต่อที่บันทึกไว้",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(0, 20))

        combo = ctk.CTkComboBox(
            main_frame,
            values=saved_connections,
            height=40,
            font=ctk.CTkFont(size=13)
        )
        combo.pack(fill="x", pady=(0, 20))
        combo.set(saved_connections[0] if saved_connections else "")

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        def on_load():
            config_name = combo.get()
            config = conn_controller.load_connection_config(config_name)
            if config:
                dialog.destroy()
                result = {
                    "name": "",
                    "host": config.host,
                    "port": config.port,
                    "username": config.username,
                    "password": config.password,
                    "identity_file": config.identity_file,
                    "protocol": config.protocol,
                    "save": False
                }
                self._process_connection(result)
            else:
                messagebox.showerror("ข้อผิดพลาด", "ไม่พบการเชื่อมต่อที่เลือก")

        def on_delete():
            config_name = combo.get()
            if messagebox.askyesno("ยืนยันการลบ", f"ลบการเชื่อมต่อ '{config_name}' หรือไม่?"):
                conn_controller.delete_saved_connection(config_name)
                dialog.destroy()
                messagebox.showinfo("สำเร็จ", "ลบการเชื่อมต่อสำเร็จ")

        ctk.CTkButton(
            button_frame,
            text="🗑️ ลบ",
            command=on_delete,
            fg_color="red",
            hover_color="darkred",
            width=80,
            height=45,
            font=ctk.CTkFont(size=13)
        ).pack(side="left")

        ctk.CTkButton(
            button_frame,
            text="ยกเลิก",
            command=dialog.destroy,
            fg_color="gray40",
            hover_color="gray30",
            width=100,
            height=45,
            font=ctk.CTkFont(size=13)
        ).pack(side="right")

        ctk.CTkButton(
            button_frame,
            text="โหลดและเชื่อมต่อ",
            command=on_load,
            width=150,
            height=45,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="right", padx=(10, 0))

    def _process_connection(self, result):
        if not result:
            return

        conn_controller = self.controller.get_connection_controller()

        success, message = conn_controller.connect(
            host=result["host"],
            port=result["port"],
            username=result["username"],
            password=result["password"],
            identity_file=result["identity_file"],
            protocol=result["protocol"]
        )

        if message == "PASSPHRASE_REQUIRED":
            passphrase_texts = {
                "title": "🔐 ต้องการ Passphrase",
                "message": "SSH Key ของคุณมีการป้องกันด้วย passphrase\nกรุณากรอก passphrase เพื่อปลดล็อก key",
                "placeholder": "กรอก passphrase...",
                "ok": "ตกลง",
                "cancel": "ยกเลิก"
            }

            passphrase_dialog = PassphraseDialog(
                self,
                passphrase_texts,
                result["identity_file"]
            )
            self.wait_window(passphrase_dialog)

            passphrase = passphrase_dialog.get_passphrase()
            if passphrase is None:
                return

            success, message = conn_controller.connect(
                host=result["host"],
                port=result["port"],
                username=result["username"],
                password=result["password"],
                identity_file=result["identity_file"],
                protocol=result["protocol"],
                passphrase=passphrase
            )

        if success:
            file_controller = self.controller.get_file_controller()
            file_controller.initialize()

            self.connection_start_time = time.time()
            self.connection_timer_running = True
            self._update_connection_timer()

            self.status_label.configure(text=f"เชื่อมต่อแล้ว: {result['host']}")
            self.sidebar.set_connected(True)
            self._enable_navigation(True)
            self._handle_refresh()

            if result["save"]:
                conn_controller.save_connection_config(
                    name=result["name"],
                    host=result["host"],
                    port=result["port"],
                    username=result["username"],
                    password=result["password"],
                    identity_file=result["identity_file"],
                    protocol=result["protocol"]
                )

            self._update_disk_usage()
            self.terminal.write_welcome(result["host"], result["username"])
        else:
            messagebox.showerror("ข้อผิดพลาดในการเชื่อมต่อ", message)

    def _handle_disconnect(self):
        self.connection_timer_running = False
        self.connection_start_time = None
        self.connection_timer_label.configure(text="")
        self.disk_usage_retry_count = 0

        self.controller.get_connection_controller().disconnect()
        self.status_label.configure(text="ตัดการเชื่อมต่อแล้ว")
        self.sidebar.set_connected(False)
        self._enable_navigation(False)
        self.remote_browser.clear()
        self.path_entry.delete(0, "end")
        self.disk_usage_label.configure(text="")
        self.terminal.clear_output()
        self.upload_btn.configure(state="disabled")
        self.download_btn.configure(state="disabled")

    def _handle_refresh(self):
        file_controller = self.controller.get_file_controller()
        files = file_controller.list_current_directory()
        self.remote_browser.set_files(files)
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, file_controller.current_path)

    def _handle_local_file_select(self, file_info):
        self.selected_local_file = file_info
        if self.controller.get_connection_controller().is_connected():
            self.upload_btn.configure(state="normal")

    def _handle_remote_file_select(self, file_info):
        self.selected_remote_file = file_info
        if self.controller.get_connection_controller().is_connected():
            self.download_btn.configure(state="normal")

    def _handle_remote_file_double_click(self, file_info):
        if file_info.is_dir:
            file_controller = self.controller.get_file_controller()
            file_controller.change_directory(file_info.path)
            self._handle_refresh()

    def _handle_context_menu(self, file_info, x, y):
        menu = ctk.CTkToplevel(self)
        menu.wm_overrideredirect(True)
        menu.geometry(f"+{x}+{y}")

        menu_frame = ctk.CTkFrame(menu)
        menu_frame.pack(fill="both", expand=True)

        def close_menu():
            menu.destroy()

        actions = []

        if not file_info.is_dir:
            actions.append(("👁️ ดูเนื้อหา", lambda: self._view_file(file_info, close_menu)))
            actions.append(("✏️ แก้ไข", lambda: self._edit_file(file_info, close_menu)))

        actions.extend([
            ("📥 ดาวน์โหลด", lambda: self._download_file(file_info, close_menu)),
            ("✏️ เปลี่ยนชื่อ", lambda: self._rename_file(file_info, close_menu)),
            ("🗑️ ลบ", lambda: self._delete_file(file_info, close_menu)),
            ("ℹ️ คุณสมบัติ", lambda: self._show_properties(file_info, close_menu))
        ])

        for text, command in actions:
            btn = ctk.CTkButton(
                menu_frame,
                text=text,
                command=command,
                fg_color="transparent",
                hover_color="gray"
            )
            btn.pack(fill="x", padx=2, pady=2)

        menu.bind("<FocusOut>", lambda e: menu.destroy())
        menu.focus_set()

    def _handle_back(self):
        file_controller = self.controller.get_file_controller()
        if file_controller.go_back():
            self._handle_refresh()

    def _handle_forward(self):
        file_controller = self.controller.get_file_controller()
        if file_controller.go_forward():
            self._handle_refresh()

    def _handle_up(self):
        file_controller = self.controller.get_file_controller()
        file_controller.go_to_parent()
        self._handle_refresh()

    def _handle_path_enter(self, event):
        path = self.path_entry.get()
        file_controller = self.controller.get_file_controller()
        file_controller.change_directory(path)
        self._handle_refresh()

    def _handle_search(self, event):
        search_text = self.search_entry.get()
        file_controller = self.controller.get_file_controller()
        file_controller.set_filter(search_text)
        self._handle_refresh()

    def _handle_upload(self):
        filename = filedialog.askopenfilename(title="เลือกไฟล์เพื่ออัปโหลด")
        if filename:
            file_controller = self.controller.get_file_controller()
            basename = os.path.basename(filename)
            success, message = file_controller.upload_file(filename, basename)

            if success:
                messagebox.showinfo("สำเร็จ", "อัปโหลดไฟล์สำเร็จ")
                self._handle_refresh()
            else:
                messagebox.showerror("ข้อผิดพลาด", message)

    def _quick_upload(self):
        if not self.selected_local_file or self.selected_local_file.is_dir:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกไฟล์เพื่ออัปโหลด")
            return

        file_controller = self.controller.get_file_controller()
        basename = os.path.basename(self.selected_local_file.path)
        success, message = file_controller.upload_file(self.selected_local_file.path, basename)

        if success:
            messagebox.showinfo("สำเร็จ", f"อัปโหลด {basename} สำเร็จ")
            self._handle_refresh()
        else:
            messagebox.showerror("ข้อผิดพลาด", message)

    def _quick_download(self):
        if not self.selected_remote_file or self.selected_remote_file.is_dir:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกไฟล์เพื่อดาวน์โหลด")
            return

        local_path = self.local_browser.current_path
        save_path = os.path.join(local_path, self.selected_remote_file.name)

        file_controller = self.controller.get_file_controller()
        success, message = file_controller.download_file(self.selected_remote_file.path, save_path)

        if success:
            messagebox.showinfo("สำเร็จ", f"ดาวน์โหลด {self.selected_remote_file.name} สำเร็จ")
            self.local_browser.refresh()
        else:
            messagebox.showerror("ข้อผิดพลาด", message)

    def _handle_new_file(self):
        dialog = ctk.CTkInputDialog(text="ชื่อไฟล์:", title="สร้างไฟล์ใหม่")
        filename = dialog.get_input()

        if filename:
            file_controller = self.controller.get_file_controller()
            success, message = file_controller.create_file(filename)

            if success:
                messagebox.showinfo("สำเร็จ", "สร้างไฟล์สำเร็จ")
                self._handle_refresh()
            else:
                messagebox.showerror("ข้อผิดพลาด", message)

    def _handle_new_folder(self):
        dialog = ctk.CTkInputDialog(text="ชื่อโฟลเดอร์:", title="สร้างโฟลเดอร์ใหม่")
        dirname = dialog.get_input()

        if dirname:
            file_controller = self.controller.get_file_controller()
            success, message = file_controller.create_directory(dirname)

            if success:
                messagebox.showinfo("สำเร็จ", "สร้างโฟลเดอร์สำเร็จ")
                self._handle_refresh()
            else:
                messagebox.showerror("ข้อผิดพลาด", message)

    def _download_file(self, file_info, callback):
        callback()
        save_path = filedialog.asksaveasfilename(
            initialfile=file_info.name,
            title="บันทึกไฟล์เป็น"
        )

        if save_path:
            file_controller = self.controller.get_file_controller()
            success, message = file_controller.download_file(file_info.path, save_path)

            if success:
                messagebox.showinfo("สำเร็จ", "ดาวน์โหลดไฟล์สำเร็จ")
            else:
                messagebox.showerror("ข้อผิดพลาด", message)

    def _rename_file(self, file_info, callback):
        callback()
        dialog = ctk.CTkInputDialog(
            text=f"เปลี่ยนชื่อ '{file_info.name}' เป็น:",
            title="เปลี่ยนชื่อ"
        )
        new_name = dialog.get_input()

        if new_name:
            file_controller = self.controller.get_file_controller()
            success, message = file_controller.rename(file_info.name, new_name)

            if success:
                messagebox.showinfo("สำเร็จ", "เปลี่ยนชื่อสำเร็จ")
                self._handle_refresh()
            else:
                messagebox.showerror("ข้อผิดพลาด", message)

    def _delete_file(self, file_info, callback):
        callback()
        if messagebox.askyesno("ยืนยันการลบ", f"ลบ '{file_info.name}' หรือไม่?"):
            file_controller = self.controller.get_file_controller()

            if file_info.is_dir:
                success, message = file_controller.delete_directory(file_info.path)
            else:
                success, message = file_controller.delete_file(file_info.path)

            if success:
                messagebox.showinfo("สำเร็จ", "ลบสำเร็จ")
                self._handle_refresh()
            else:
                messagebox.showerror("ข้อผิดพลาด", message)

    def _view_file(self, file_info, callback):
        callback()
        file_controller = self.controller.get_file_controller()
        success, content = file_controller.read_file(file_info.path)

        if not success:
            messagebox.showerror("ข้อผิดพลาด", content)
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"ดูเนื้อหา: {file_info.name}")
        dialog.geometry("800x600")

        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        textbox = ctk.CTkTextbox(
            main_frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="none"
        )
        textbox.pack(fill="both", expand=True)
        textbox.insert("1.0", content)
        textbox.configure(state="disabled")

        ctk.CTkButton(
            main_frame,
            text="ปิด",
            command=dialog.destroy,
            width=100,
            height=35
        ).pack(pady=(10, 0))

    def _edit_file(self, file_info, callback):
        callback()
        file_controller = self.controller.get_file_controller()
        success, content = file_controller.read_file(file_info.path)

        if not success:
            messagebox.showerror("ข้อผิดพลาด", content)
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"แก้ไข: {file_info.name}")
        dialog.geometry("800x600")

        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        textbox = ctk.CTkTextbox(
            main_frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="none"
        )
        textbox.pack(fill="both", expand=True, pady=(0, 10))
        textbox.insert("1.0", content)

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        def save_content():
            new_content = textbox.get("1.0", "end-1c")
            success, message = file_controller.write_file(file_info.path, new_content)

            if success:
                messagebox.showinfo("สำเร็จ", "บันทึกไฟล์สำเร็จ")
                dialog.destroy()
                self._handle_refresh()
            else:
                messagebox.showerror("ข้อผิดพลาด", message)

        ctk.CTkButton(
            button_frame,
            text="บันทึก",
            command=save_content,
            width=100,
            height=35
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            button_frame,
            text="ยกเลิก",
            command=dialog.destroy,
            fg_color="gray40",
            hover_color="gray30",
            width=100,
            height=35
        ).pack(side="right")

    def _show_properties(self, file_info, callback):
        callback()
        props = f"""ชื่อ: {file_info.name}
เส้นทาง: {file_info.path}
ขนาด: {file_info.get_size_str()}
สิทธิ์: {file_info.permissions}
แก้ไขล่าสุด: {file_info.modified_time.strftime('%Y-%m-%d %H:%M:%S')}
ประเภท: {'โฟลเดอร์' if file_info.is_dir else 'ไฟล์'}"""

        messagebox.showinfo("คุณสมบัติ", props)

    def _handle_terminal_command(self, command):
        if command.strip().lower() == "clear":
            self.terminal.clear_output()
            return

        ssh_conn = self.controller.get_connection_controller().get_connection()
        stdout, stderr, exit_code = ssh_conn.execute_command(command)

        if stdout:
            self.terminal.append_output(stdout, "output")
        if stderr:
            self.terminal.append_output(f"\nError: {stderr}\n", "error")

        if exit_code != 0:
            self.terminal.append_output(f"\nExit code: {exit_code}\n", "error")

    def _handle_language_change(self, lang: str):
        from views.language import lang_manager

        if "ไทย" in lang or "🇹🇭" in lang:
            lang_manager.set_language("thai")
        else:
            lang_manager.set_language("english")

        self.sidebar.update_language(lang_manager.texts)
        messagebox.showinfo("Info", f"Language changed to: {lang}\n(Full translation coming soon!)")

    def _handle_appearance_change(self, mode: str):
        ctk.set_appearance_mode(mode)

    def _on_directory_changed(self, path: str):
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, path)

    def _enable_navigation(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.back_btn.configure(state=state)
        self.forward_btn.configure(state=state)
        self.up_btn.configure(state=state)

    def _update_disk_usage(self):
        try:
            file_controller = self.controller.get_file_controller()
            usage = file_controller.get_disk_usage()

            if usage["total"] == 0:
                if self.disk_usage_retry_count < 3:
                    self.disk_usage_label.configure(text="กำลังโหลดข้อมูลดิสก์...")
                    self.disk_usage_retry_count += 1
                    self.after(2000, self._update_disk_usage)
                else:
                    self.disk_usage_label.configure(text="")
                return

            self.disk_usage_retry_count = 0
            total_gb = usage["total"] / (1024 ** 3)
            used_gb = usage["used"] / (1024 ** 3)
            free_gb = usage["free"] / (1024 ** 3)
            percent = (used_gb / total_gb * 100) if total_gb > 0 else 0

            self.disk_usage_label.configure(
                text=f"พื้นที่: {used_gb:.1f}GB / {total_gb:.1f}GB ({percent:.1f}%) - ว่าง: {free_gb:.1f}GB"
            )
        except Exception as e:
            self.disk_usage_label.configure(text="")

    def _update_connection_timer(self):
        if not self.connection_timer_running or self.connection_start_time is None:
            return

        elapsed = time.time() - self.connection_start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)

        if hours > 0:
            time_str = f"⏱ เชื่อมต่อแล้ว: {hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            time_str = f"⏱ เชื่อมต่อแล้ว: {minutes:02d}:{seconds:02d}"

        self.connection_timer_label.configure(text=time_str)
        self.after(1000, self._update_connection_timer)
