import base64


def generate_auth_frag():
    raw = "%s:%s" % (raw_input('Username: '), raw_input('Password: '))
    auth_frag = base64.urlsafe_b64encode(raw)
    with open('auth_frag.txt', 'w') as fh:
        fh.write(auth_frag)

if __name__ == '__main__':
    generate_auth_frag()
