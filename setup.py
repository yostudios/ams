from distutils.core import setup

setup(name="ams", version="0.4",
      url="http://yo.se/",
      author="Yo AB", author_email="opensource@yo.se",
      license="3-clause BSD <http://www.opensource.org/licenses/bsd-license.php>",
      description="Painless queue management",
      packages=["ams", "ams.platsbanken", "ams.unemployee",
                "ams.unemployee.handlers"])
