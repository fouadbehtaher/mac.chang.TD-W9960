import subprocess
import random
import time
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QPushButton, QTextEdit, QSpinBox, 
                             QGroupBox, QSystemTrayIcon, QMenu, QAction, QMessageBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QFont

class MACChangerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_mac = "1C:3B:F3:E0:2A:8C"
        self.original_mac = self.current_mac
        self.timer = QTimer()
        self.timer.timeout.connect(self.change_mac)
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("أداة تغيير عنوان MAC تلقائيًا")
        self.setGeometry(300, 300, 500, 600)
        
        # إنشاء الويدجيت المركزي
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # معلومات العنوان الحالي
        info_group = QGroupBox("معلومات العنوان الحالي")
        info_layout = QVBoxLayout()
        
        self.mac_label = QLabel(f"العنوان الحالي: {self.current_mac}")
        self.mac_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addWidget(self.mac_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # إعدادات التغيير التلقائي
        settings_group = QGroupBox("إعدادات التغيير التلقائي")
        settings_layout = QVBoxLayout()
        
        # فترة التغيير
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("فترة التغيير (دقائق):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 120)
        self.interval_spin.setValue(10)
        interval_layout.addWidget(self.interval_spin)
        settings_layout.addLayout(interval_layout)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # الأزرار
        buttons_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("بدء التغيير التلقائي")
        self.start_btn.clicked.connect(self.start_auto_change)
        buttons_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("إيقاف التغيير التلقائي")
        self.stop_btn.clicked.connect(self.stop_auto_change)
        self.stop_btn.setEnabled(False)
        buttons_layout.addWidget(self.stop_btn)
        
        self.change_once_btn = QPushButton("تغيير مرة واحدة")
        self.change_once_btn.clicked.connect(self.change_mac)
        buttons_layout.addWidget(self.change_once_btn)
        
        self.restore_btn = QPushButton("استعادة العنوان الأصلي")
        self.restore_btn.clicked.connect(self.restore_original_mac)
        buttons_layout.addWidget(self.restore_btn)
        
        layout.addLayout(buttons_layout)
        
        # سجل التغييرات
        log_group = QGroupBox("سجل التغييرات")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # إضافة نص إلى السجل
        self.add_log("تم تشغيل الأداة")
        self.add_log(f"العنوان الأصلي: {self.original_mac}")
        
        # إنشاء أيقونة النظام
        self.create_tray_icon()
        
    def create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("network-wireless"))
        
        show_action = QAction("إظهار", self)
        quit_action = QAction("خروج", self)
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(QApplication.quit)
        
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def add_log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def generate_random_mac(self):
        # إنشاء عنوان MAC عشوائي
        mac = [0x1C, 0x3B, 0xF3,  # OUI part (يمكن تعديله حسب الراوتر)
               random.randint(0x00, 0x7F),
               random.randint(0x00, 0xFF),
               random.randint(0x00, 0xFF)]
        return ':'.join(map(lambda x: "%02x" % x, mac)).upper()
    
    def change_mac(self):
        new_mac = self.generate_random_mac()
        self.current_mac = new_mac
        self.mac_label.setText(f"العنوان الحالي: {self.current_mac}")
        
        # هنا سيتم وضع الكود الفعلي لتغيير عنوان MAC على النظام
        # هذا مثال للتنفيذ على أنظمة Linux (يتطلب صلاحيات root)
        try:
            # تعطيل الواجهة أولاً
            subprocess.call(["sudo", "ifconfig", "wlan0", "down"])
            # تغيير عنوان MAC
            subprocess.call(["sudo", "ifconfig", "wlan0", "hw", "ether", new_mac])
            # تفعيل الواجهة مرة أخرى
            subprocess.call(["sudo", "ifconfig", "wlan0", "up"])
            
            self.add_log(f"تم تغيير العنوان إلى: {new_mac}")
            self.tray_icon.showMessage("تم تغيير عنوان MAC", 
                                      f"العنوان الجديد: {new_mac}", 
                                      QSystemTrayIcon.Information, 2000)
        except Exception as e:
            self.add_log(f"خطأ في تغيير العنوان: {str(e)}")
    
    def restore_original_mac(self):
        self.current_mac = self.original_mac
        self.mac_label.setText(f"العنوان الحالي: {self.current_mac}")
        
        try:
            # تعطيل الواجهة أولاً
            subprocess.call(["sudo", "ifconfig", "wlan0", "down"])
            # استعادة عنوان MAC الأصلي
            subprocess.call(["sudo", "ifconfig", "wlan0", "hw", "ether", self.original_mac])
            # تفعيل الواجهة مرة أخرى
            subprocess.call(["sudo", "ifconfig", "wlan0", "up"])
            
            self.add_log(f"تم استعادة العنوان الأصلي: {self.original_mac}")
            self.tray_icon.showMessage("تم استعادة عنوان MAC", 
                                      f"العنوان الأصلي: {self.original_mac}", 
                                      QSystemTrayIcon.Information, 2000)
        except Exception as e:
            self.add_log(f"خطأ في استعادة العنوان: {str(e)}")
    
    def start_auto_change(self):
        interval_minutes = self.interval_spin.value()
        interval_ms = interval_minutes * 60 * 1000
        
        self.timer.start(interval_ms)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        self.add_log(f"بدأ التغيير التلقائي كل {interval_minutes} دقائق")
        self.tray_icon.showMessage("بدأ التغيير التلقائي", 
                                  f"سيتم تغيير العنوان كل {interval_minutes} دقائق", 
                                  QSystemTrayIcon.Information, 2000)
        
        # تغيير فوري عند البدء
        self.change_mac()
    
    def stop_auto_change(self):
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        self.add_log("تم إيقاف التغيير التلقائي")
        self.tray_icon.showMessage("تم إيقاف التغيير التلقائي", 
                                  "توقف تغيير العنوان التلقائي", 
                                  QSystemTrayIcon.Information, 2000)
    
    def closeEvent(self, event):
        if self.timer.isActive():
            reply = QMessageBox.question(self, 'تأكيد الإغلاق',
                                         'التغيير التلقائي لا يزال نشطاً. هل تريد حقاً الخروج؟',
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.stop_auto_change()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    window = MACChangerApp()
    window.show()
    
    sys.exit(app.exec_())
