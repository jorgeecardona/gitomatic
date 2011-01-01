import unittest
from os import path, environ
import shutil
import tempfile


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
            self._directory, '.gitomatic/conf.d')))
        self.assertTrue(path.exists(path.join(
            self._directory, '.gitomatic/repos')))

    def test_add_repo(self):

        self.gitomatic.initialize()
        self.gitomatic.repo_add('test.git')

        self.assertTrue(path.exists(path.join(
            self._directory, '.gitomatic/repos/test.git')))

    def test_delete_repo(self):

        # Add repo
        self.gitomatic.initialize()
        self.gitomatic.repo_add('test.git')
        self.assertTrue(path.exists(path.join(
            self._directory, '.gitomatic/repos/test.git')))

        # Delete repo
        self.gitomatic.repo_delete('test.git')
        self.assertTrue(not path.exists(path.join(
            self._directory, '.gitomatic/repos/test.git')))

    def test_add_key(self):

        # Initialize repo.
        self.gitomatic.initialize()

        from hashlib import sha1
        key = 'ssh-rsa asasdav asda'
        hash_1 = sha1(key).hexdigest()
        hash_2 = self.gitomatic.key_add('test@test.com', key)
        self.assertEqual(hash_1, hash_2)

