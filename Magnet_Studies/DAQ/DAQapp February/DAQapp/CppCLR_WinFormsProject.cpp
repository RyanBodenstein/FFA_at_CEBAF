#include "pch.h"

#include <windows.h>
#using <System.dll>
#include "synchapi.h"
#include <string>
#include <vector>
#include <msclr\marshal_cppstd.h>
#include <sstream>
#include <iostream>
#include <fstream>
#include <time.h>


// int main(array<System::String ^> ^args)
// {
//    return 0;
// }
using namespace System;

using namespace System::IO::Ports;

class PortDataReceived
{
public:
    static void Reader(std::vector<std::string>& input, System::String^ port)
    {
        SerialPort^ mySerialPort = gcnew SerialPort(port);
        int i1 = 0;
        bool contread = true;
        System::Windows::Forms::DialogResult msgboxID;
        mySerialPort->BaudRate = 3000000;
        mySerialPort->Parity = Parity::None;
        mySerialPort->StopBits = StopBits::One;
        mySerialPort->DataBits = 8;
        mySerialPort->Handshake = Handshake::None;
        mySerialPort->RtsEnable = true;
        mySerialPort->ReadTimeout = 500;
        

        //mySerialPort->DataReceived += gcnew SerialDataReceivedEventHandler(DataReceivedHandler);
        //Console::WriteLine("Setting up");
        mySerialPort->Open();
        //Console::WriteLine("Writing B");
        mySerialPort->WriteLine("t");
        //Console::WriteLine("Begin Waiting");
        Sleep(70);
        //Console::WriteLine("End Waiting, Writing S");
        //mySerialPort->WriteLine("S");
        //Console::WriteLine("Reading Data");
        
            std::string indata = msclr::interop::marshal_as < std::string>(mySerialPort->ReadLine());
            input.push_back(indata);
        

        //Console::Write("DataLength: ");
        //Console::WriteLine(indata->Length);
        i1 = 0;
        while (contread) {
            try {
          //      Console::WriteLine(indata);
 
                std::string indata1 = msclr::interop::marshal_as <std::string>( mySerialPort->ReadLine());
                Sleep(5);
                input.push_back(indata1);
                //input = input+indata;
             //   dataout.push_back(indata);
            //    Console::Write("DataLength: ");
            //    Console::WriteLine(indata->Length);
            }
            catch (TimeoutException^ ex) {
                contread = false;
                //Console::WriteLine("End of Buffer");
            }
        }
        //Console::WriteLine("Data read");
        //Console::WriteLine("Press any key to continue...");
        //Console::WriteLine();
        //Console::ReadKey();
        mySerialPort->Close();
        //Console::WriteLine("Port Closed");
    }

public:
    static void ArdReader(std::vector<std::string>& input)
    {
        SerialPort^ mySerialPort = gcnew SerialPort("COM4");
        int i1 = 0;
        bool contread = true;
        mySerialPort->BaudRate = 9600;
        mySerialPort->Parity = Parity::None;
        mySerialPort->StopBits = StopBits::One;
        mySerialPort->DataBits = 8;
        mySerialPort->Handshake = Handshake::None;
        mySerialPort->RtsEnable = true;
        mySerialPort->ReadTimeout = 1000;


        //mySerialPort->DataReceived += gcnew SerialDataReceivedEventHandler(DataReceivedHandler);
        //Console::WriteLine("Setting up");
        mySerialPort->Open();
        //Console::WriteLine("Writing B");
        mySerialPort->WriteLine("B");
        //Console::WriteLine("Begin Waiting");
        Sleep(60);
        //Console::WriteLine("End Waiting, Writing S");
        mySerialPort->WriteLine("S");
        //Console::WriteLine("Reading Data");
        std::string indata = msclr::interop::marshal_as < std::string>(mySerialPort->ReadLine());
        input.push_back(indata);
        //Console::Write("DataLength: ");
        //Console::WriteLine(indata->Length);
        i1 = 0;
        while (contread) {
            try {
                //      Console::WriteLine(indata);

                std::string indata1 = msclr::interop::marshal_as <std::string>(mySerialPort->ReadLine());
                Sleep(5);
                input.push_back(indata1);
                //input = input+indata;
             //   dataout.push_back(indata);
            //    Console::Write("DataLength: ");
            //    Console::WriteLine(indata->Length);
            }
            catch (TimeoutException^ ex) {
                contread = false;
                //Console::WriteLine("End of Buffer");
            }
        }
        //Console::WriteLine("Data read");
        //Console::WriteLine("Press any key to continue...");
        //Console::WriteLine();
        //Console::ReadKey();
        mySerialPort->Close();
        //Console::WriteLine("Port Closed");
    }

    public:
        static void Ardmessagereceive(std::vector<std::string>& input,System::String^ port, System::String^ message)
        {
            SerialPort^ mySerialPort = gcnew SerialPort(port);
            int i1 = 0;
            bool contread = true;
            bool isopen = true;
            mySerialPort->BaudRate = 9600;
            mySerialPort->Parity = Parity::None;
            mySerialPort->StopBits = StopBits::One;
            mySerialPort->DataBits = 8;
            mySerialPort->Handshake = Handshake::None;
            mySerialPort->RtsEnable = true;
            mySerialPort->ReadTimeout = 100;
            

            //mySerialPort->DataReceived += gcnew SerialDataReceivedEventHandler(DataReceivedHandler);
            //Console::WriteLine("Setting up");
           
                mySerialPort->Open();
            
            //Console::WriteLine("Writing B");
            if (isopen) {
                mySerialPort->WriteLine(message);
                Sleep(50);
                //mySerialPort->WriteLine("B");
                //Console::WriteLine("Begin Waiting");

                //Console::WriteLine("End Waiting, Writing S");
                //mySerialPort->WriteLine("S");
                //Console::WriteLine("Reading Data");
                std::string indata = msclr::interop::marshal_as < std::string>(mySerialPort->ReadLine());
                input.push_back(indata);
                //Console::Write("DataLength: ");
                //Console::WriteLine(indata->Length);
                i1 = 0;
                while (contread) {
                    try {
                        //      Console::WriteLine(indata);

                        std::string indata1 = msclr::interop::marshal_as <std::string>(mySerialPort->ReadLine());
                        Sleep(50);
                        input.push_back(indata1);
                        //input = input+indata;
                     //   dataout.push_back(indata);
                    //    Console::Write("DataLength: ");
                    //    Console::WriteLine(indata->Length);
                    }
                    catch (TimeoutException^ ex) {
                        contread = false;
                        //Console::WriteLine("End of Buffer");
                    }
                }
                //Console::WriteLine("Data read");
                //Console::WriteLine("Press any key to continue...");
                //Console::WriteLine();
                //Console::ReadKey();
                mySerialPort->Close();
            }
            //Console::WriteLine("Port Closed");
        }
            public:
                static void Ardmessage(System::String^ port, System::String^ message)
                {
                    SerialPort^ mySerialPort = gcnew SerialPort(port);
                    int i1 = 0;
                    bool contread = true;
                    bool isopen = true;
                    mySerialPort->BaudRate = 9600;
                    mySerialPort->Parity = Parity::None;
                    mySerialPort->StopBits = StopBits::One;
                    mySerialPort->DataBits = 8;
                    mySerialPort->Handshake = Handshake::None;
                    mySerialPort->RtsEnable = true;
                    mySerialPort->ReadTimeout = 1000;


                    //mySerialPort->DataReceived += gcnew SerialDataReceivedEventHandler(DataReceivedHandler);
                    //Console::WriteLine("Setting up");
                    
                        mySerialPort->Open();
                    
                    //Console::WriteLine("Writing B");
                    if (isopen) {
                        mySerialPort->WriteLine(message);
                        Sleep(120);
                        //mySerialPort->WriteLine("B");
                        //Console::WriteLine("Begin Waiting");

                        //Console::WriteLine("End Waiting, Writing S");
                        //mySerialPort->WriteLine("S");
                        //Console::WriteLine("Reading Data");
                        /*
                        std::string indata = msclr::interop::marshal_as < std::string>(mySerialPort->ReadLine());
                        input.push_back(indata);
                        //Console::Write("DataLength: ");
                        //Console::WriteLine(indata->Length);
                        i1 = 0;
                        while (contread) {
                            try {
                                //      Console::WriteLine(indata);

                                std::string indata1 = msclr::interop::marshal_as <std::string>(mySerialPort->ReadLine());
                                Sleep(5);
                                input.push_back(indata1);
                                //input = input+indata;
                             //   dataout.push_back(indata);
                            //    Console::Write("DataLength: ");
                            //    Console::WriteLine(indata->Length);
                            }
                            catch (TimeoutException^ ex) {
                                contread = false;
                                //Console::WriteLine("End of Buffer");
                            }
                        }
                        //Console::WriteLine("Data read");
                        //Console::WriteLine("Press any key to continue...");
                        //Console::WriteLine();
                        //Console::ReadKey();*/
                        mySerialPort->Close();
                        //Console::WriteLine("Port Closed");
                    }
                }
        public:
            static void ArdLights(System::String^ port)
            {
                SerialPort^ mySerialPort = gcnew SerialPort(port);
                int i1 = 0;
                bool contread = true;
                mySerialPort->BaudRate = 9600;
                mySerialPort->Parity = Parity::None;
                mySerialPort->StopBits = StopBits::One;
                mySerialPort->DataBits = 8;
                mySerialPort->Handshake = Handshake::None;
                mySerialPort->RtsEnable = true;
                mySerialPort->ReadTimeout = 500;


                //mySerialPort->DataReceived += gcnew SerialDataReceivedEventHandler(DataReceivedHandler);
                //Console::WriteLine("Setting up");
                mySerialPort->Open();
                //Console::WriteLine("Writing B");
                //mySerialPort->WriteLine(message);
                //Sleep(50);
                mySerialPort->WriteLine("lp1on");
                Sleep(1100);
                mySerialPort->WriteLine("lp2on");
                Sleep(1100);
                mySerialPort->WriteLine("lp3on");
                //Console::WriteLine("Begin Waiting");
                Sleep(1100);
                //Console::WriteLine("End Waiting, Writing S");
                //mySerialPort->WriteLine("S");
                //Console::WriteLine("Reading Data");
                //std::string indata = msclr::interop::marshal_as < std::string>(mySerialPort->ReadLine());
                //input.push_back(indata);
                //Console::Write("DataLength: ");
                //Console::WriteLine(indata->Length);
                //i1 = 0;
                /*
                while (contread) {
                    try {
                        //      Console::WriteLine(indata);

                        std::string indata1 = msclr::interop::marshal_as <std::string>(mySerialPort->ReadLine());
                        Sleep(5);
                        input.push_back(indata1);
                        //input = input+indata;
                     //   dataout.push_back(indata);
                    //    Console::Write("DataLength: ");
                    //    Console::WriteLine(indata->Length);
                    }
                    catch (TimeoutException^ ex) {
                        contread = false;
                        //Console::WriteLine("End of Buffer");
                    }
                }*/
                //Console::WriteLine("Data read");
                //Console::WriteLine("Press any key to continue...");
                //Console::WriteLine();
                //Console::ReadKey();
                mySerialPort->Close();
                //Console::WriteLine("Port Closed");
            }

private:
    static void DataReceivedHandler(
        Object^ sender,
        SerialDataReceivedEventArgs^ e)
    {
        SerialPort^ sp = (SerialPort^)sender;
        String^ indata = sp->ReadExisting();
        //Console::WriteLine("Data Received:");
        //Console::WriteLine(indata);
    }
};

void Tabparse(std::string input, std::string& Bx, std::string& By, std::string& Bz, std::string& Th )
{
    int ip, icl;
    int clpos[3];
    double hoyr, min, sec;
    

    icl = 0;
    for (ip = 0; ip < input.length(); ip++) {
        if (input.substr(ip, 1) == "\t") {
            clpos[icl] = ip;
            icl++;
        }
    }
    //cout<<endl<<input<<'\t'<<sppos[0]<<'\t'<<sppos[1]<<'\t'<<sppos[2]<<'\t'<<slpos[0]<<'\t'<<slpos[1]<<'\t'<<slpos[2]<<'\n';

    //cout<<endl;
    Bx = input.substr(0, clpos[0]);
  
    By = (input.substr(clpos[0] + 1, (clpos[1] - 1) - (clpos[0])));

    Bz = (input.substr(clpos[1] + 1, (clpos[2] - 1) - (clpos[1])));

    Th = (input.substr(clpos[2] + 1, input.length() - clpos[2]));

    
}

void Dashparse(std::string input, std::string& Type, std::string& plate, std::string& slot)
{
    int ip, icl;
    int clpos[3];



    icl = 0;
    for (ip = 0; ip < input.length(); ip++) {
        if (input.substr(ip, 1) == "-" && icl<2) {
            clpos[icl] = ip;
            icl++;
        }
    }
    //cout<<endl<<input<<'\t'<<sppos[0]<<'\t'<<sppos[1]<<'\t'<<sppos[2]<<'\t'<<slpos[0]<<'\t'<<slpos[1]<<'\t'<<slpos[2]<<'\n';

    //cout<<endl;
    Type = input.substr(0, clpos[0]);

    plate = (input.substr(clpos[0] + 1, (clpos[1] - 1) - (clpos[0])));

    slot = (input.substr(clpos[1] + 1, (clpos[2] - 1) - (clpos[1])));

}

void ardparse(std::string input, int& front, int& side, int& top)
{
    int ip, icl;
    int clpos[2];
    double hoyr, min, sec;
    std::stringstream scratch1, scratch2, scratch3;

    icl = 0;
    for (ip = 0; ip < input.length(); ip++) {
        if (input.substr(ip, 1) == ",") {
            clpos[icl] = ip;
            icl++;
        }
    }
    //cout<<endl<<input<<'\t'<<sppos[0]<<'\t'<<sppos[1]<<'\t'<<sppos[2]<<'\t'<<slpos[0]<<'\t'<<slpos[1]<<'\t'<<slpos[2]<<'\n';

    //cout<<endl;
    scratch1 << input.substr(0, clpos[0]);
    scratch1 >> front;
    //cout<<hoyr<<'\t';
    scratch2 << (input.substr(clpos[0] + 1, (clpos[1] - 1) - (clpos[0])));
    scratch2 >> side;
    //cout<<min<<'\t';
    scratch3 << (input.substr(clpos[1] + 1, input.length() - clpos[1]));
    scratch3 >> top;
    //cout<<sec<<'\t';
    //cout<<endl;
}

//using namespace std;
std::vector<std::string> dataout;
std::vector<std::string> ardataout;
bool wedge=false;
bool wedgesetup = false;
bool wedgedos = false;
bool wedgerod = false;
bool wedgeas = false;
bool wedgeah = false;
bool readsam = false;
bool readdos = false;
bool readrod = false;
bool readcal = false;
int fco = -1, sco = -1, tco = -1;
int afco = -1, asco = -1, atco = -1;
int ahtco = -1, ahsco = -1, ahfco = -1;
#include "Form1.h"
using namespace System::Windows::Forms;

[STAThread]
int main()
{
  Application::EnableVisualStyles();
  Application::SetCompatibleTextRenderingDefault(false);
  Application::Run(gcnew CppCLRWinFormsProject::Form1());
  return 0;
}