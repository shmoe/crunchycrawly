from subprocess import check_output
import setuptools

with open("README.md", "r") as fi:
	long_description = fi.read()

tags = check_output("git tag --points-at HEAD", shell=True, text=True).split()

if tags and tags[0]:
	version = tags[0].strip()
else:
	tags = check_output('git log --pretty=format:"%h" -n 1', shell=True, text=True).split()
	version = tags[0].strip()

tags = check_output('git log --pretty=format:"%an\t%ae" -n 1', shell=True, text=True).split('\t')

setuptools.setup(
	name="crunchycrawly",
	version=version,
	author=tags[0].strip(),
	author_email=tags[1].strip(),
	description="crawls bookmarked crunchyroll series for new content",
	long_description=long_description,
	url="https://github.com/shmoe/crunchycrawly",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
		"Operating System :: OS Independent"
	],
	license="GPLv3+",
	python_requires=">=3.7"
)
