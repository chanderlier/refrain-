from PyQt5.Qt import *
import sys
import pymysql


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("登陆界面")
        self.setWindowIcon(QIcon("./icon.ico"))
        self.resize(500, 200)
        self.Co_Width = 40
        self.Co_Heigth = 20
        self.setup_ui()
    
    def setup_ui(self):
        self.lab_l = QLabel("帐户:", self)  # 帐户标签
        self.Lin_l = QLineEdit(self)  # 帐户录入框
        self.lab_p = QLabel("密码:", self)  # 密码标签
        self.Lin_p = QLineEdit(self)  # 密码录入框
        self.Lin_p.setEchoMode(QLineEdit.Password)  # 设置密文显示
        self.Pu_l = QPushButton("登陆", self)  # 登陆按钮
        self.Pu_l.clicked.connect(self.Login)
    
    def resizeEvent(self, evt):  # 重新设置控件座标事件
        # 帐户标签
        self.lab_l.resize(self.Co_Width, self.Co_Heigth)
        self.lab_l.move(self.width() / 3, self.height() / 5)
        # 帐户录入框
        self.Lin_l.move(self.lab_l.x() + self.lab_l.width(), self.lab_l.y())
        # 密码标签
        self.lab_p.resize(self.Co_Width, self.Co_Heigth)
        self.lab_p.move(self.lab_l.x(), self.lab_l.y() + self.lab_l.height() * 2)
        # 密码录入框
        self.Lin_p.move(self.lab_p.x() + self.lab_p.width(), self.lab_p.y())
        # 登陆按钮
        self.Pu_l.move(self.Lin_p.x() + self.Lin_p.width() / 4, self.lab_p.y() + self.lab_p.width())
    
    def Login(self):
        user = self.Lin_l.text()
        pwd = self.Lin_p.text()
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='hello123',
                                    db='test', charset='utf8')
        self.cursor = self.conn.cursor()
        r = self.cursor.execute('select name,password from user where username = %s and passwd = %s',(user,pwd))
        if user == '':
            OK = QMessageBox.warning(self, ("警告"), ("""请输入账号！"""))
        if pwd == '':
            OK = QMessageBox.warning(self, ("警告"), ("""请输入密码！"""))
        if r != 1:
            print("login failed!")
        if user != '' and pwd != '':
            self.second_window = Second(user, pwd)
            self.Lin_l.setText('')
            self.Lin_p.setText('')
            self.second_window.show()
            

class Second(QWidget):
    def __init__(self, user, password, user_id=None):
        super().__init__()
        self.setWindowTitle("账户详情")
        self.setWindowIcon(QIcon("./icon.ico"))
        self.resize(500, 200)
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='hello123',
                                    db='test', charset='utf8')
        self.cursor = self.conn.cursor()
        self.input = QLineEdit(self)
        self.input.resize(200, 50)
        self.setup_ui(user, password, user_id)
        
    def setup_ui(self, user, password, user_id):
        self.Ch_l = QPushButton("充值", self)
        self.Ba_l = QPushButton("返回", self)
        if user_id:
            sql = '''
            SELECT amount FROM user WHERE id = {}
            '''.format(user_id)
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            amount = result[0]
        else:
            sql = '''
                SELECT id, amount FROM user WHERE name = {} AND password = {}
                '''.format(user, password)
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            user_id = result[0]
            amount = result[1]
        self.input.setText(str(amount))
        self.cursor.close()
        self.Ba_l.clicked.connect(self.close)
        self.Ch_l.clicked.connect(lambda: self.charge(user_id, amount))
        
    def resizeEvent(self, evt):
        self.Ch_l.move(0, 100)
        self.Ba_l.move(0, 50)
        
    def charge(self, user_id, amount):
        self.close()
        self.charge_window = Third(user_id, amount)
        self.charge_window.show()
        

class Third(QWidget):
    def __init__(self, user_id, amount):
        super().__init__()
        self.setWindowTitle("充值页面")
        self.setWindowIcon(QIcon("./icon.ico"))
        self.resize(500, 200)
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='hello123',
                                    db='test', charset='utf8')
        self.cursor = self.conn.cursor()
        self.setup_ui(user_id, amount)
        
    def setup_ui(self, user_id, amount):
        self.lab_l = QLabel("充值金额:", self)
        self.Lin_l = QLineEdit(self)
        self.Pu_l = QPushButton("确认", self)
        self.Pu_l.clicked.connect(lambda: self.charge(user_id, amount))
        
    def resizeEvent(self, evt):
        self.lab_l.resize(40, 20)
        self.lab_l.move(self.width() / 3, self.height() / 5)
        self.Lin_l.move(self.lab_l.x() + self.lab_l.width(), self.lab_l.y())
        self.Pu_l.move(self.Lin_l.x() + self.Lin_l.width() / 4, self.lab_l.y() + self.lab_l.width())
        
    def charge(self, user_id, amount):
        enter = self.Lin_l.text()
        total = amount + int(enter)
        sql = '''
        UPDATE user SET amount = {} WHERE id = {}
        '''.format(total, user_id)
        self.cursor.execute(sql)
        self.cursor.execute('commit;')
        self.cursor.close()
        OK = QMessageBox.warning(self, ("通知"), ("""充值成功 充值金额：{} 元""".format(enter)))
        self.close()
        self.second_window = Second(None, None, user_id)
        self.second_window.show()
        

if __name__ == '__main__':
    App = QApplication(sys.argv)
    Win = Window()
    Win.show()
    sys.exit(App.exec_())
