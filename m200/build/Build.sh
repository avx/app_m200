#!/bin/sh

ROOT_DIR="/usr/local/m200";
BUILD_DIR=${ROOT_DIR}"/build";

cd $BUILD_DIR && tar -zxvf Python-3.3.2.tar.gz && cd $BUILD_DIR/Python-3.3.2 && ./configure --prefix=$ROOT_DIR --exec-prefix=$ROOT_DIR && make -j4 && make install

cd $BUILD_DIR && tar -zxvf tornado-3.2.2.tar.gz && cd $BUILD_DIR/tornado-3.2.2 && ${ROOT_DIR}/bin/python3 setup.py build && ${ROOT_DIR}/bin/python3 setup.py install

cd $BUILD_DIR && tar -zxvf scomm-0.8.5-av.tar.gz && cd $BUILD_DIR/scomm-0.8.5-av && ./configure LDFLAGS=-lpthread CXXFLAGS=-fpermissive --bindir=${ROOT_DIR}/bin --sbindir=${ROOT_DIR}/bin && make && make install

grep -q "m200:" /etc/aliases
if [ $? -ne 0 ]; then
	echo 'm200: tmg@enforta.com,cuss.oper@enforta.com' >> /etc/aliases
	newaliases
fi;

ln -s /usr/local/m200/bin/clear_logs /etc/cron.daily/clear_logs

ln -s /usr/local/m200/bin/m200mon /etc/init.d/m200mon

chkconfig --add m200mon

chkconfig m200mon on

chown -R root:root /usr/local/m200

chown -R mmsvc_sys:mmsvc /usr/local/m200/log

chmod o-rx /usr/local/m200/bin/m200srv /usr/local/m200/bin/m200mon /usr/local/m200/bin/act/*

chmod mmsvc_sys:mmsvc /usr/local/m200/etc/*.ini

chmod o-r /usr/local/m200/etc/*.ini

chmod o-r /usr/local/m200/log/*.log

chown -R root:root /usr/local/m200/log
