echo deploying contact_sites to pip...
git add .
set /p commit=Enter commit message: 
git commit -m "%commit%"
echo bumping version...
set /p category=Enter bump category patch, minor or major: 
python ./setup.py --version > version_temp
set /p version=< version_temp
del version_temp
bumpversion --current-version %version% %category% ./setup.py
echo clean dist...
mkdir .\dist\old
mv .\dist\* .\dist\old
echo build dist...
python setup.py sdist bdist_wheel
rm .\dist\old -R
git add .
git commit -m "bumping version %version% with %category%"
git push
echo uploading to pip...
twine upload dist/*