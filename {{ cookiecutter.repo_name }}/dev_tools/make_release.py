"""
make cli tool to make a release of the package.

Based on:
https://blog.danslimmon.com/2019/07/15/do-nothing-scripting-the-key-to-gradual-automation/
And:
https://github.com/alan-turing-institute/sktime/blob/main/build_tools/make_release.py
"""
import os, re, sys, logging
from pathlib import Path
import colorama
import toml
from pkg_resources import packaging

logging.basicConfig()

PCKG_NAME = "{{ cookiecutter.python_package }}"
project_info = toml.load("pyproject.toml")["project"]

def wait_for_enter():
    input("Press Enter to continue: ")

def ask_for_confirmation(question):
    """
    Ask the user for confirmation.
    """
    answer = input(question + " [y/n]: ")
    while answer and (answer.lower()[0] not in ["y", "n"]):
        answer = input("Please answer y or n: ")
    return answer.lower()[0] == "y"

def colored(msg, color=None, style=None):
    colors = {
        "red": colorama.Fore.RED,
        "green": colorama.Fore.GREEN,
        "cyan": colorama.Fore.CYAN,
        "yellow": colorama.Fore.YELLOW,
        "magenta": colorama.Fore.MAGENTA,
        None: "",
    }
    styles = {
        "bright": colorama.Style.BRIGHT,
        "dim": colorama.Style.DIM,
        None: "",
    }
    pre = colors[color] + styles[style]
    post = colorama.Style.RESET_ALL
    return f"{pre}{msg}{post}"


def cprint(msg, color=None, style=None):
    """Coloured printing"""
    print(colored(msg, color=color, style=style))  # noqa


def wait_for_enter():
    input(colored("\nPress Enter to continue", style="dim"))
    print()  # noqa


def find_package_version():
    """
    Validate that the release is valid.
    """
    pyproject = open("pyproject.toml", "r").read()
    pyproject_version_match = re.search(r"^version = ['\"]([^'\"]*)['\"]", pyproject, re.M)
    if not pyproject_version_match:
        logging.info("Unable to find version in pyproject.toml. Returning {{ cookiecutter.python_package }}.__version__.")
        from {{ cookiecutter.python_package }}.__init__ import __version__
        return __version__
    pyproject_version = pyproject_version_match.group(1)
    if packaging.version.parse(pyproject_version) != packaging.version.parse(__version__):
        logging.warning("Version mismatch between {{ cookiecutter.python_package }}.__version__ and pyproject.toml")
        logging.warning(f"Returning {pyproject_version=}")
    return str(pyproject_version)

def find_git_branch():
    git_branch = None
    if Path(".git").is_dir():
        head_dir = Path(".") / ".git" / "HEAD"
        with head_dir.open("r") as f: 
            content = f.read().splitlines()
        for line in content:
            if line[0:4] == "ref:":
                git_branch = line.partition("refs/heads/")[2]
    return git_branch

def find_latest_pip_version(pckg_name):
    """
    Find the latest pip version.
    """
    import subprocess
    pip_version = subprocess.check_output(
        ["pip", "index", "versions", pckg_name], universal_newlines=True
    )
    pip_version = re.search("Available versions: ([0-9]*\.[0-9]*\.[0-9]*)", pip_version).group(1)
    return pip_version

class Step:

    confirmation_msg = None
    
    def pre(self, context):
        pass

    def post(self, context):
        wait_for_enter()

    def run(self, context):
        try:
            self.pre(context)
            if self.confirm_action():
                self.action(context)
            self.post(context)
        except KeyboardInterrupt:
            cprint("\nInterrupted.", color="red")
            raise SystemExit(1)
        except Exception as e:
            cprint(f"Error on {self.__class__.__name__} step: {e}", color="red")
            raise SystemExit(1)

    @staticmethod
    def instruct(msg):
        cprint(msg, color="green")

    def confirm_action(self):
        if self.confirmation_msg:
            if not ask_for_confirmation(self.confirmation_msg):
                cprint("Skipping.", color="yellow")
                return False
        return True

    def print_run(self, msg):
        cprint("Run:", color="cyan", style="bright")
        self.print_cmd(msg)

    @staticmethod
    def print_cmd(msg):
        cprint("\t" + msg, color="cyan", style="bright")

    @staticmethod
    def do_cmd(cmd):
        cprint(f"Going to run: {cmd}", color="magenta", style="bright")
        wait_for_enter()
        os.system(cmd)

    def action(self, context):
        raise NotImplementedError("abstract method")

class ConfirmGitStatus(Step):
    def __init__(self, branch):
        self.branch = branch

    def action(self, context):
        current_brach = find_git_branch()
        assert current_brach == self.branch, f"Current git branch is \"{current_brach}\", expected \"{self.branch}\""
        self.instruct(
            f"Make sure you're on: {self.branch} branch, that "
            f"branch is up-to-date, and all new changes are merged "
            f"in."
        )
        self.do_cmd(f"git checkout {self.branch}")
        self.do_cmd("git pull")

class ValidateVersions(Step):
    """
    Validate that the release is valid.
    """
    def action(self, context):
        from {{ cookiecutter.python_package }}.__init__ import __version__
        self.instruct("Validating that the release versions are valid.")
        pyproject = open("pyproject.toml", "r").read()
        pyproject_version_match = re.search(r"^version = ['\"]([^'\"]*)['\"]", pyproject, re.M)
        pyproject_version = pyproject_version_match.group(1)
        assert packaging.version.parse(pyproject_version) == packaging.version.parse(__version__), \
            "Version mismatch between {{ cookiecutter.python_package }}._meta.__version__ and pyproject.toml"

class BumpVersion(Step):
    """
    Bump the {{ cookiecutter.python_package }} version in pyproject.toml and {{ cookiecutter.python_package }}/_meta.py.
    """
    confirmation_msg = f"__init__.py and pyproject.toml need to be updated with a new {PCKG_NAME} version. Do you want me to do it?"

    def action(self,context):
        from {{ cookiecutter.python_package }}.__init__ import __version__
        pyproject = open("pyproject.toml", "r").read()
        pyproject_version_match = re.search(r"^version = ['\"]([^'\"]*)['\"]", pyproject, re.M)
        pyproject_version = pyproject_version_match.group(1)
        pyproject_version = packaging.version.parse(pyproject_version)

        if pyproject_version != packaging.version.parse(__version__):
            raise Exception("Version mismatch between pyhandy.__version__ and pyproject.toml")

        bumped_micro = pyproject_version.micro + 1
        bumped_version = packaging.version.parse(f"{pyproject_version.major}.{pyproject_version.minor}.{bumped_micro}")
        pyproject = pyproject.replace(pyproject_version_match.group(1), str(bumped_version))
        
        self.instruct(f"Bumping version in pyproject.toml and {{ cookiecutter.python_package }}/__init__.py from {pyproject_version} to {bumped_version}")

        with open("pyproject.toml", "w") as pyproject_file:
            pyproject_file.write(pyproject)
        with open("{{ cookiecutter.python_package }}/__init__.py", "r") as meta:
            init_content = meta.read()
        init_content = init_content.replace(__version__, str(bumped_version))
        with open("{{ cookiecutter.python_package }}/__init__.py", "w") as meta:
            meta.write(init_content)
        context["bumped_version"] = bumped_version
    
    def post(self, context):
        if context.get("bumped_version", False):
            self.instruct("You should now commit the changes.")
            self.do_cmd("git add pyproject.toml {{ cookiecutter.python_package }}/__init__.py")
            self.do_cmd(f"git commit -m 'Patched version to {context['bumped_version']}'")
        current_version = find_package_version()
        self.instruct(f"Current {PCKG_NAME} version is {current_version}")
        if context["version"] != current_version:
            context["version"] = current_version
        super().post(context)

class MakeClean(Step):
    def action(self, context):
        self.do_cmd("make clean")

class MakeDocs(Step):
    def action(self, context):
        self.do_cmd("make docs")

class GitTagRelease(Step):
    def action(self, context):
        self.instruct("Tagging version as a release")
        self.do_cmd(f"git tag v{context['version']}")

class VerifyPipLatestVersion(Step):
    def action(self, context):
        self.instruct("Verifying that the latest version is up-to-date")
        latest_version = find_latest_pip_version(PCKG_NAME)
        latest_version = packaging.version.parse(latest_version)
        current_version = packaging.version.parse(context["version"])
        assert current_version > latest_version, f"The current listed version of {PCKG_NAME} ({current_version}) is not newer than its latest available version ({latest_version})"
        self.instruct(f"Latest version of {PCKG_NAME} is {latest_version}. Current version is {current_version}")

class PushToGitHub(Step):
    def action(self, context):
        self.instruct("Add and commit your changes with git, then push the repo")

if __name__ == "__main__":
    context = dict(
        name=PCKG_NAME,
        version=find_package_version(),
    )
    for step in [
        # ConfirmGitStatus("main"), # If a git repo
        ValidateVersions(),
        BumpVersion(),
        MakeClean(),
        MakeDocs(),
        # GitTagRelease(), # If a git repo
        # VerifyPipLatestVersion(), # If pip installable
        PushToGitHub(),
    ]:
        step.run(context)
    BumpVersion()
    print("Release is valid.")