site:
	mkdocs build

serve:
	mkdocs serve

theme:
	sass --style compressed source/main.scss writethedocs/css/main.css

deploy: site
	rsync -ru site/ root@szm.me:~/blog/
