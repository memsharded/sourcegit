from conans import ConanFile, CMake
from conans.tools import load, save, mkdir
import subprocess
import os
import shutil


CONAN_GIT_URL_FILE = "_conan_git_url"

def _generate_commit():
    command = "git log -1"
    try:
        output = subprocess.check_output(command).decode().strip()
    except Exception:
        return
    line = output.splitlines()[0]
    _, commit = line.split()
    location = os.getcwd() # this could be the remote URL from git remote
    save(CONAN_GIT_URL_FILE, "%s %s" % (location, commit))

_generate_commit()


class HelloConan(ConanFile):
    name = "Hello"
    version = "0.1"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"
    exports_sources = CONAN_GIT_URL_FILE

    def source(self):
        git = load(CONAN_GIT_URL_FILE)
        url, commit = git.split()
        tmp = os.path.join(self.source_folder, "tmp_src")
        self.run("git clone %s tmp_src" % url)
        self.run("cd tmp_src && git checkout %s" % commit)
        for r, dirs, files in os.walk("tmp_src"):
            dirs[:] = [d for d in dirs if d != ".git"] 
            for f in files:
                filepath = os.path.join(self.source_folder, r, f)
                relpath = os.path.join(self.source_folder, os.path.relpath(filepath, tmp))
                mkdir(os.path.dirname(relpath))
                shutil.copy(filepath, relpath)
        shutil.rmtree("tmp_src")


    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="src")
        cmake.build()

    def package(self):
        self.copy("*.h", dst="include", src="src")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.dylib*", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["hello"]
