class Database():

    def __init__(self, engine, config):
        # init the database connection for MySQL or PostgreSQL
        if engine == 'mysql':
            import MySQLdb
            self.connection = MySQLdb.connect(**config)
        elif engine == 'postgresql':
            import psycopg
            self.connection = psycopg.connect(**config)

    def get_password_map(self):
        # fetch all users and password hashes from the database
        cursor = self.connection.cursor()
        cursor.execute('SELECT username, password FROM auth_user;')
        rows = cursor.fetchall()

        # create map for the password_hashes
        password_map = {}
        for row in rows:
            username, password_hash = row[0:2]

            # skip non sha512 hashes
            if password_hash.startswith('crypt_sha512$6$'):
                password_map[username] = password_hash.replace('crypt_sha512$6$', '$6$')
            else:
                password_map[username] = None

        return password_map
