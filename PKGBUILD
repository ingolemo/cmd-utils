pkgname=cmd-utils
pkgver=0.1
pkgrel=1
pkgdesc="Assorted general purpose scripts"
arch=(any)
url="http://github.com/ingolemo/cmd-utils"
license=('GPL')
depends=(bash python rsync coreutils findutils gawk sed python-docopt)
optdepends=('openssh: backup to remote location')
source=("$pkgname::git+http://github.com/ingolemo/cmd-utils")

package() {
	cd $srcdir/cmd-utils
	for file in *.py *.sh; do
		msg "Installing $file"
		install -Dm744 "$file" "$pkgdir"/usr/bin/"${file%.*}"
	done
}
