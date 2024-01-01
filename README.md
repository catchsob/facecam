# facecam
A face recognition suite on variant platform

### fagen.py

to generate a face encoding csv file

1. prepare jpg face image files with labeled file name (such as chou.jpg, wang.jpg, ... etc) in specific directory (such as train)
2. generate the face encoding file by command "python3 facegen.py -p train"
3. "python3 facegen.py --help" to get usage

### faceme.py

to register a face via cam picturing

1. a camera on Windows or Pi Camera on Jetson Nano/ Raspberry Pi is necessary.
2. start the face picturing and registering by command "python3 faceme.py"
3. "python3 faceme.py --help" to get usage

### facecam.py

to recognize the face by cam (realtime) or picture (batch)

1. prepare jpg face image files (such as 001.jpg) in specific directory (such as test)
2. recognize the image file by command "python3 facecam.py -p test/001.jpg"
3. if camera on Windows or Pi Camera is installed on Jetson Nano/ Raspberry Pi, you may run realtime face recognition by command "python3 facecam.py"
4. "python3 facecam.py --help" to get usage

### rollcall_edge.py

to roll call based on face recognition

1. start the application by command "python3 rollcall_edge.py -m mqtt_ip_address"
2. button to "註冊" register for a new user
3. button to "點名" sign-in for an existing user
4. "python3 rollcall_edge.py --help" to get usage

##### platforms

Microsoft Windows 10/ NVIDIA Jetson Nano/ Raspberry Pi 3B+

##### dependencies

dlib, pillow, opencv (facecam, faceme, rollcall_edge), numpy, face_recognition, python3-tk (faceme, rollcall_edge), paho-mqtt (rollcall_edge)

##### installation process on Windows 10

1. install CMake
2. install Visual Studio Community with both MSVC v14x and Windows 10 SDK (or Windows 11 SDK) checked within Desktop development with C++
3. pip install dlib
4. pip install face_recognition paho-mqtt
5. get all codes in this project
6. get TaipeiSansTCBeta-Regular.ttf

##### notes

You should download and specify Chinese font (such as TaipeiSansTCBeta-Regular.ttf from https://sites.google.com/view/jtfoundry/en) especially on Respberry Pi. "-f YOUR_CHINESEFONT.ttf" in facecam.py or rollcall_edge is suggested.
