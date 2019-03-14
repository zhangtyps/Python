#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : openvpn_manager.py
@Time : 2019/03/11 16:08:05
@Author : zhangtyps
@GitHub : https://github.com/zhangtyps
@Version : 1.1
@Desc : 生成随机密码，自动创建或删除openvpn账户，生成用户证书（pexpect交互式操作示例）
'''

# here put the import lib
import pexpect, sys, random, string, os, re, shutil


class openvpn(object):
    def __init__(self, user):
        self.user = user
        self.ldap_pwd = 'redhat'
        self.ca_pwd = '7wg7QLyvNM8rVMT^'
        self.aldif_path = '/mnt/a.ldif'
        self.cmd_path = '/etc/openvpn/easy-rsa/2.0/'

    def add_account(self):
        modify_file(self.user, self.aldif_path)
        pwd = create_random_passwd()
        create_account(self.user, self.ldap_pwd, self.aldif_path)
        set_passwd(self.user, pwd)
        create_cert(self.user, self.ca_pwd, self.cmd_path)

    def renew_cert(self):
        create_cert(self.user, self.ca_pwd, self.cmd_path)

    def del_account(self):
        delete_account(self.user, self.ldap_pwd)


#修改a.ldif文件
def modify_file(user, filepath):
    file1 = None
    with open(filepath, 'r') as f:
        file1 = f.read()
    #提取在文本中原来的用户名，替换并重新写入文件
    old_name = re.search(r'dn: uid=(.*?),', file1).group(1)
    file1 = re.sub(old_name, user, file1)
    try:
        with open(filepath, 'w') as f:
            f.write(file1)
    except:
        print('写入 ' + filepath + ' 异常，请检查执行权限是否足够！')
        sys.exit()


#创建openvpn账户
def create_account(user, ldap_passwd, filepath):
    #读取文件路径创建账户
    cmd1 = 'ldapadd -x -D "cn=admin,dc=test,dc=com" -W -f ' + filepath
    p1 = pexpect.spawn(cmd1)
    p1.expect('Enter LDAP Password')
    p1.sendline(ldap_passwd)
    #判断用户创建成功与否
    index = p1.expect(['Already exists', pexpect.EOF, pexpect.TIMEOUT])
    if index == 0:
        print('已存在同名账户，' + user + ' 账户开通失败！')
        sys.exit()
    elif index == 1:
        #print(user + '账户开通成功！')
        pass
    else:
        print('创建用户异常，请检查openvpn运行情况！')
        sys.exit()


#设置账户密码
def set_passwd(user, passwd):
    cmd2 = '/usr/bin/ldappasswd -x -S -D "cn=admin,dc=test,dc=com" -W uid=' + user + ',ou=People,dc=test,dc=com'
    p2 = pexpect.spawn(cmd2)  #指定输出的到控制台上
    p2.expect('New password')
    p2.sendline(passwd)
    p2.expect('Re-enter new password')
    p2.sendline(passwd)
    p2.expect('Enter LDAP Password')
    p2.sendline('redhat')
    p2.expect(pexpect.EOF)
    #输出结果
    print('账户开通成功：\n' + user + '\n' + passwd)
    write_txt(user, passwd)


#创建openvpn证书
def create_cert(cert_name, ca_passwd, vpn_filepath):
    os.chdir(vpn_filepath)
    cmd = '/bin/bash -c "source ./vars && ./build-key ' + cert_name + '"'
    p = pexpect.spawn(cmd, encoding='utf-8')
    #p.logfile = sys.stdout
    p.expect('Country Name')
    p.sendline('')
    p.expect('State or Province Name')
    p.sendline('')
    p.expect('Locality Name')
    p.sendline('')
    p.expect('Organization Name')
    p.sendline('')
    p.expect('Organizational Unit Name')
    p.sendline('')
    p.expect('Common Name')
    p.sendline('')
    p.expect('Name')
    p.sendline('')
    p.expect('Email Address')
    p.sendline('')
    p.expect('challenge password')
    p.sendline(ca_passwd)
    p.expect('An optional company name')
    p.sendline('')
    p.expect('Sign the certificate')
    p.sendline('y')
    index = p.expect(
        ['requests certified, commit', 'failed to update database'])
    if index == 0:
        p.sendline('y')
    else:
        print('证书创建失败！\n可能存在同名证书或该名称证书曾创建过，请修改证书名称后重新创建！')
    p.expect(pexpect.EOF)
    print('证书创建成功！')


#生成随机密码
def create_random_passwd(length=16):
    #随机密码库
    chars = string.ascii_letters + string.digits + '!@#$%^&*'
    output_passwd = ''
    for i in range(length):
        output_passwd += random.choice(chars)
    return output_passwd


#删除openvpn账户
def delete_account(user, ldap_passwd):
    cmd = 'ldapdelete -x -W -D "cn=admin,dc=test,dc=com"  "uid=' + user + ',ou=People,dc=test,dc=com"'
    p1 = pexpect.spawn(cmd)
    p1.expect('Enter LDAP Password')
    p1.sendline(ldap_passwd)
    index = p1.expect(['No such object', pexpect.EOF])
    if index == 0:
        print(user + ' 无此账户!')
    else:
        print(user + ' 账户删除成功!')
    pass


def write_txt(user, passwd):
    with open('ps.txt', 'w') as f:
        f.write(user + '\n' + passwd)


def move_cert(cert_name, cert_path='/etc/openvpn/easy-rsa/2.0/keys/', destination_path='/home/zhangyps/'):
    shutil.move(cert_path + cert_name + '.crt', destination_path)
    shutil.move(cert_path + cert_name + '.csr', destination_path)
    shutil.move(cert_path + cert_name + '.key', destination_path)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('''参数介绍:
        ./vpn.py -a user1 新开user1账户和证书
        ./vpn.py -d user2 创建一个名为user2证书
        ./vpn.py -c user3 删除用户user3
        【因未检测到参数，进入交互模式！】
        请输入对应数字编号使用功能：
            1)  新开账户和证书
            2)  证书续期
            3)  删除用户
            4)  退出
        ''')
        r = int(input('请输入数字：'))
        if r == 1:
            r1 = input('请输入新开用户名（英文和数字）：')
            o1 = openvpn(r1)
            o1.add_account()
            move_cert(r1)
        elif r == 2:
            r1 = input('请输入证书名（英文和数字）：')
            o1 = openvpn(r1)
            o1.renew_cert()
            move_cert(r1)
        elif r == 3:
            r1 = input('请输入要删除的用户名：')
            o1 = openvpn(r1)
            o1.del_account()
        else:
            sys.exit()
    elif len(sys.argv) == 3:
        #参数模式
        user=sys.argv[2]
        if sys.argv[1]=='-a':
            o1 = openvpn(user)
            o1.add_account()
            move_cert(user)
        if sys.argv[1]=='-c':
            o1 = openvpn(user)
            o1.renew_cert()
            move_cert(user)
        if sys.argv[1]=='-d':
            o1 = openvpn(user)
            o1.del_account()
    else:
        pass

