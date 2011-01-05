import unittest
from os import path, environ
import shutil
import tempfile
from hashlib import sha1


class GitomaticTestCase(unittest.TestCase):

    def setUp(self):

        # Change home path for a temporary one.
        self._directory = tempfile.mkdtemp()
        environ['HOME'] = self._directory
        from gitomatic.base import Gitomatic
        self.gitomatic = Gitomatic()

    def tearDown(self):
        # Delete temporary directory
        shutil.rmtree(self._directory)

    def test_initialize_gitomatic(self):

        self.gitomatic.initialize()

        self.assertTrue(path.exists(path.join(
            self._directory, '.ssh')))
        self.assertTrue(path.exists(path.join(
            self._directory, '.gitomatic')))
        self.assertTrue(path.exists(path.join(
            self._directory, '.gitomatic/keys')))
        self.assertTrue(path.exists(path.join(
            self._directory, '.gitomatic/repositories')))

    def test_add_repo(self):

        self.gitomatic.initialize()
        self.gitomatic.repo_add('test.git')

        self.assertTrue(path.exists(path.join(
            self._directory, '.gitomatic/repositories/test.git')))

    def test_delete_repo(self):

        # Add repo
        self.gitomatic.initialize()
        self.gitomatic.repo_add('test.git')
        self.assertTrue(path.exists(path.join(
            self._directory, '.gitomatic/repositories/test.git')))

        # Delete repo
        self.gitomatic.repo_delete('test.git')
        self.assertTrue(not path.exists(path.join(
            self._directory, '.gitomatic/repositories/test.git')))

    def test_add_key(self):

        # Initialize repo.
        self.gitomatic.initialize()

        key = 'ssh-rsa asasdav asda'
        hash_1 = sha1(key).hexdigest()
        hash_2 = self.gitomatic.key_add('test@test.com', key)
        self.assertEqual(hash_1, hash_2)
        self.assertTrue(path.exists(path.join(
            self._directory, '.gitomatic/keys/test@test.com:%s' % (hash_1, ))))

    def test_delete_key(self):

        # Initialize repo.
        self.gitomatic.initialize()

        key = 'ssh-rsa asasdav asda'
        hash_ = self.gitomatic.key_add('test@test.com', key)
        self.assertTrue(path.exists(path.join(
            self._directory, '.gitomatic/keys/test@test.com:%s' % (hash_, ))))

        self.gitomatic.key_delete('test@test.com', hash_)
        self.assertTrue(not path.exists(path.join(
            self._directory, '.gitomatic/keys/test@test.com:%s' % (hash_, ))))

    def test_add_and_read_perm(self):

        # Initialize repo.
        self.gitomatic.initialize()
        self.gitomatic.repo_add('test.git')
        self.gitomatic.perm_add('test@test.com', 'test', 'R')

        self.assertTrue(
            'R' in self.gitomatic.perm_read('test@test.com', 'test'))

        self.assertTrue(not
            'W' in self.gitomatic.perm_read('test@test.com', 'test'))

        self.gitomatic.perm_add('test@test.com', 'test', 'W')

        self.assertTrue(
            'R' in self.gitomatic.perm_read('test@test.com', 'test'))

        self.assertTrue(
            'W' in self.gitomatic.perm_read('test@test.com', 'test'))

    def test_delete_perm(self):

        # Initialize repo.
        self.gitomatic.initialize()
        self.gitomatic.repo_add('test.git')
        self.gitomatic.perm_add('test@test.com', 'test', 'RW')

        self.assertTrue(
            'R' in self.gitomatic.perm_read('test@test.com', 'test'))

        self.assertTrue(
            'W' in self.gitomatic.perm_read('test@test.com', 'test'))

        self.gitomatic.perm_delete('test@test.com', 'test', 'R')

        self.assertTrue(not
            'R' in self.gitomatic.perm_read('test@test.com', 'test'))

        self.assertTrue(not
            'W' in self.gitomatic.perm_read('test@test.com', 'test'))
