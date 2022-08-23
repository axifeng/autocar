cd paddlelite
rm -rdf build
python3 setup.py build
cp build/lib.linux-aarch64-3.5/*.so ../
