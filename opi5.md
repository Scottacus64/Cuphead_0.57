# Install Armbian 23.02 Jammy Gnome Desktop

- Download from https://www.armbian.com/orangepi-5/
- Install with username `mpf` and password `orange` 

# Enable 3D Acceleration:

```
sudo add-apt-repository ppa:liujianfeng1994/panfork-mesa
sudo add-apt-repository ppa:liujianfeng1994/rockchip-multimedia
sudo apt update
sudo apt -y dist-upgrade
sudo apt -y install mali-g610-firmware rockchip-multimedia-config
```

# Reboot

```
sudo reboot
```

# Install development tools

```
sudo apt-get -y install  build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
```

# Install MPF dependencies

```
sudo apt-get -y install libsdl2-dev libsdl2-ttf-dev libsdl2-image-dev libsdl2-mixer-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-base gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly libgstreamer1.0-dev libxine2-ffmpeg libsmpeg-dev libswscale-dev libavformat-dev libavcodec-dev libavdevice-dev libavfilter-dev libjpeg-dev libtiff5-dev libx11-dev libmtdev-dev libgl1-mesa-dev libgles2-mesa-dev pulseaudio lsb-release
```

# Download, compile, install Python 3.9.1, remove source

*Do not install any other version of Python 3.9.x as the MPF text console will not display*

```
wget https://www.python.org/ftp/python/3.9.1/Python-3.9.1.tgz
tar -xf Python-3.9.1.tgz
cd Python-3.9.1
./configure --enable-optimizations
make -j 8
sudo make altinstall
cd ..
sudo rm -rf  Python-3.9.1
rm Python-3.9.1.tgz
```

# Install MPF

```
sudo pip3.9 install "mpf[all]" grpcio==1.36.0 grpcio-tools==1.36.0
sudo pip3.9 install "mpf-mc[all]"
```

# Test MPF

*Adapted from https://docs.missionpinball.org/tutorial/2_creating_a_new_machine.html*

```
mkdir your_machine
cd your_machine
mkdir config
echo "#config_version=5" > config/config.yaml  
mpf -b
```

# Install QT6 dependencies

*Adapted from https://doc.qt.io/qt-6/linux-building.html and https://www.ics.com/blog/how-build-qt-640-source-ubuntu-linux*

```
sudo apt install -y cmake bison build-essential clang flex gperf libatspi2.0-dev libbluetooth-dev libclang-dev libcups2-dev libdrm-dev libegl1-mesa-dev libfontconfig1-dev libfreetype6-dev libgstreamer1.0-dev libhunspell-dev libnss3-dev libopengl-dev libpulse-dev libssl-dev libts-dev libx11-dev libx11-xcb-dev libxcb-glx0-dev libxcb-icccm4-dev libxcb-image0-dev libxcb-keysyms1-dev libxcb-randr0-dev libxcb-render-util0-dev libxcb-shape0-dev libxcb-shm0-dev libxcb-sync-dev libxcb-util-dev libxcb-xfixes0-dev libxcb-xinerama0-dev libxcb-xkb-dev libxcb1-dev libxcomposite-dev libxcursor-dev libxdamage-dev libxext-dev libxfixes-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev libxkbfile-dev libxrandr-dev libxrender-dev libxshmfence-dev libxshmfence1 llvm llvm-dev ninja-build nodejs python-is-python3 python3
```

# Download, compile, install QT 6.4.2, remove source 

*Takes about 2 hours*

```
wget https://download.qt.io/official_releases/qt/6.4/6.4.2/single/qt-everywhere-src-6.4.2.tar.xz
tar xvf qt-everywhere-src-6.4.2.tar.xz
cd qt-everywhere-src-6.4.2
./configure -prefix /usr/local/Qt6
cmake --build . --parallel
sudo cmake --install .
cd ..
sudo rm -rf qt-everywhere-src-6.4.2
rm qt-everywhere-src-6.4.2.tar.xz
```

# Upgrade PIP

```
sudo /usr/local/bin/python3.9 -m pip install --upgrade pip
```

# Prebuild PyQt6  

*Required because PyQt6 is asking questions that can't be answered during pip3*
*Takes about 1 hour*

```
sudo PATH=/usr/local/Qt6/bin:$PATH pip3.9 install PyQt6 --config-settings --confirm-license= --verbose
```

# Install MPF Monitor

```
sudo pip3.9 install "mpf-monitor[all]"
```

# Make Image Of SD Card (MacOS)

```
diskutil list  

/dev/disk4 (external, physical):
   #:                       TYPE NAME                    SIZE       IDENTIFIER
   0:      GUID_partition_scheme                        *128.2 GB   disk4
   1: BC13C2FF-59E6-4262-A352-B275FD6F7172               268.4 MB   disk4s1
   2:           Linux Filesystem                         127.9 GB   disk4s2

sudo dd if=/dev/disk4 of=mpf.img bs=1m
```

# Make Image Of SD Card (Linux)

```
fdisk -l

Disk /dev/mmcblk1: 119.38 GiB, 128177930240 bytes, 250347520 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: gpt
Disk identifier: 1303EA25-A12A-7546-9CD5-D81C74EF55FE

Device          Start       End   Sectors   Size Type
/dev/mmcblk1p1  32768    557055    524288   256M Linux extended boot
/dev/mmcblk1p2 557056 247824384 247267329 117.9G Linux filesystem

sudo dd if=/dev/mmcblk1 of=mpf.img bs=1m
```

# Shrink SD Card (Docker)

```
docker run --privileged=true --rm --volume $(pwd):/workdir mgomesborges/pishrink pishrink -Zv mpf.img mpf_copy_small.img
```
