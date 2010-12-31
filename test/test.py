import unittest
from os import path, environ
import shutil
import tempfile


class GitomaticTestCase(unittest.TestCase):

    def setUp(self):

        # Change home path for a temporary one.
        self._directory = tempfile.mkdtemp()
        environ['HOME'] = self._directory

    def tearDown(self):
        # Delete temporary directory
        shutil.rmtree(self._directory)

    def test_initialize_gitomatic(self):

        from gitomatic import main
        main.init(None)

        self.assertTrue(path.exists(path.join(
            self._directory, '.ssh')))
        self.assertTrue(path.exists(path.join(
            self._directory, '.gitomatic')))
        self.assertTrue(path.exists(path.join(
            self._directory, '.gitomatic/keys')))
        self.assertTrue(path.exists(path.join(
            self._directory, '.gitomatic/conf.d')))
        self.assertTrue(path.exists(path.join(
            self._directory, '.gitomatic/conf.d/000-global')))
        self.assertTrue(path.exists(path.join(
            self._directory, '.gitomatic/repos')))

    def test_add_repo(self):

        from gitomatic import repo
        repo.add('test.git')

        self.assertTrue(path.exists(path.join(
            self._directory, '.gitomatic/repos/test.git')))

    def test_remove_repo(self):

        from gitomatic import repo
        repo.add('test.git')

        self.assertTrue(path.exists(path.join(
            self._directory, '.gitomatic/repos/test.git')))

        repo.remove('test.git')
        self.assertTrue(not path.exists(path.join(
            self._directory, '.gitomatic/repos/test.git')))


if __name__ == '__main__':
    unittest.main()
