import subprocess
import sys
from distutils import log
from distutils.errors import DistutilsExecError
from distutils.file_util import copy_file
from distutils.sysconfig import customize_compiler
from pathlib import Path

from setuptools import Command, setup
from setuptools.command.build_py import build_py as origin_build_py
from setuptools.dist import Distribution


class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""

    def has_ext_modules(self):
        return True


class build_py(origin_build_py):
    def run(self):
        self.run_command('build_kt')
        return super().run()


class build_kt(Command):
    user_options = [('kt-libraries=', None, ''),
                    ('shared-location=', None, "copy the shared libraries here after linking."), ]

    def initialize_options(self) -> None:
        self.build_lib = None
        self.shared_location = None
        self.kt_libraries = None
        self.compiler = None

    def finalize_options(self) -> None:
        pass

    # def get_source_files(self) -> List[str]:
    #     return []

    # def get_outputs(self) -> List[str]:
    #     return list(self.get_output_mapping().keys())

    # def get_output_mapping(self) -> Dict[str, str]:
    #     mapping = {}

    #     shared_localtion = Path("{build_lib}") / self.shared_location

    #     for (lib_name, build_info) in self.kt_libraries:
    #         build_dir = self.get_kt_build_dir(lib_name)

    #         if sys.platform == 'win32':
    #             libname = f"{lib_name}.dll"  # windows
    #         elif sys.platform == 'darwin':
    #             libname = f"{lib_name}.dylib"  # macOS
    #         else:
    #             libname = f"{lib_name}.so"  # unix/linux

    #         mapping[shared_localtion / libname] = build_dir / libname

    #         mapping[shared_localtion / f"{lib_name}.processed.h"] = build_dir / f"{lib_name}.processed.h"

    #     return mapping

    def get_kt_build_dir(self, lib_name, build_info):
        build_dir = Path(build_info.get("root"))
        if (subproject := build_info.get("subproject", None)) is not None:
            build_dir = build_dir / subproject
        build_dir = build_dir / "build" / "bin" / "native" / "releaseShared"
        return build_dir

    def build_sharedlib(self):
        out_dir = (Path("build/lib") / self.shared_location).absolute()
        out_dir.mkdir(exist_ok=True, parents=True)

        for (lib_name, build_info) in self.kt_libraries:
            log.info("building '%s' Kotlin/Native Shared Library", lib_name)

            root = Path(build_info.get("root")).absolute()
            if sys.platform == 'win32':
                gradlew = "gradlew.bat"
            else:
                gradlew = "gradlew"

            task = ""
            if (subproject := build_info.get("subproject", None)) is not None:
                task += f":{subproject}:"
            task += "linkReleaseSharedNative"

            if sys.platform == 'win32':
                cmd = f"{gradlew} {task}"
            else:
                cmd = f"./{gradlew} {task}"

            log.info(f"running {cmd} (in {root})")
            call_return = subprocess.call(cmd, shell=True, cwd=root)
            if call_return != 0:
                raise DistutilsExecError(f"gradlew returned an non-zero value {call_return}")

            build_dir = self.get_kt_build_dir(lib_name, build_info)

            if sys.platform == 'win32':
                lib_filename = f"{lib_name}.dll"  # windows
            elif sys.platform == 'darwin':
                lib_filename = f"{lib_name}.dylib"  # macOS
            else:
                lib_filename = f"{lib_name}.so"  # unix/linux

            copy_file(str((build_dir / lib_filename).absolute()), str(out_dir))

    def run(self):
        self.build_sharedlib()


setup(
    name="mahjong-utils",
    version="0.2.0a1",
    author="ssttkkl",
    author_email="huang.wen.long@hotmail.com",
    license="MIT",
    url="https://github.com/ssttkkl/mahjong-utils",
    readme="README.md",
    install_requires=[
        "pydantic>=1.9.0",
        "cffi>=1.15.1",
        "stringcase>=1.2.0"
    ],
    packages=[
        "mahjong_utils",
        "mahjong_utils.lib",
        "mahjong_utils.models",
        "mahjong_utils.yaku"
    ],
    package_data={"": ["*_api.i"]},
    options={
        "build_kt": {
            "kt_libraries": [
                ("libmahjongutils",
                 {
                     "root": "kt",
                     "subproject": "mahjong-utils-native-sharedlib"
                 })
            ],
            "shared_location": "mahjong_utils/lib"
        }
    },
    cmdclass={"build_kt": build_kt, "build_py": build_py},
    distclass=BinaryDistribution,
)
