#pragma once

namespace CppCLRWinFormsProject {

	using namespace System;
	using namespace System::ComponentModel;
	using namespace System::Collections;
	using namespace System::Windows::Forms;
	using namespace System::Data;
	using namespace System::Drawing;

	/// <summary>
	/// Summary for Form1
	/// </summary>
	public ref class Form1 : public System::Windows::Forms::Form
	{
	public:
		Form1(void)
		{
			InitializeComponent();
			//
			//TODO: Add the constructor code here
			//
		}

	protected:
		/// <summary>
		/// Clean up any resources being used.
		/// </summary>
		~Form1()
		{
			if (components)
			{
				delete components;
			}
		}
	private: System::Windows::Forms::Button^ button1;
	private: System::Windows::Forms::Label^ label1;
	private: System::Windows::Forms::TextBox^ textBox1;
	private: System::Windows::Forms::Button^ button2;
	private: System::Windows::Forms::TextBox^ textBox2;
	private: System::Windows::Forms::Button^ button3;
	private: System::Windows::Forms::TextBox^ textBox3;
	private: System::Windows::Forms::Label^ label2;
	private: System::Windows::Forms::Label^ label3;
	private: System::Windows::Forms::Label^ label4;
	private: System::Windows::Forms::Label^ label5;
	private: System::Windows::Forms::TextBox^ textBox4;
	private: System::Windows::Forms::TextBox^ textBox5;
	private: System::Windows::Forms::TextBox^ textBox6;
	private: System::Windows::Forms::TextBox^ textBox7;
	private: System::Windows::Forms::TextBox^ textBox8;
	private: System::Windows::Forms::CheckBox^ checkBox1;
	private: System::Windows::Forms::CheckBox^ checkBox2;
	private: System::Windows::Forms::CheckBox^ checkBox3;
	private: System::Windows::Forms::TextBox^ textBox9;
	private: System::Windows::Forms::TextBox^ textBox10;
	private: System::Windows::Forms::TextBox^ textBox11;
	private: System::Windows::Forms::TextBox^ textBox12;
	private: System::Windows::Forms::Label^ label6;
	private: System::Windows::Forms::Label^ label7;
	private: System::Windows::Forms::Label^ label8;
	private: System::Windows::Forms::Label^ label9;
	private: System::Windows::Forms::TextBox^ textBox13;
	private: System::Windows::Forms::TextBox^ textBox14;
	private: System::Windows::Forms::TextBox^ textBox15;
	private: System::Windows::Forms::TextBox^ textBox16;
	private: System::Windows::Forms::Label^ label10;
	private: System::Windows::Forms::Label^ label11;
	private: System::Windows::Forms::Label^ label12;
	private: System::Windows::Forms::Label^ label13;
	private: System::Windows::Forms::Button^ button4;
	private: System::Windows::Forms::Button^ button5;
	private: System::Windows::Forms::TextBox^ textBox17;
	private: System::Windows::Forms::Button^ button6;
	private: System::Windows::Forms::ProgressBar^ progressBar1;
	private: System::Windows::Forms::GroupBox^ groupBox1;
	private: System::Windows::Forms::TextBox^ textBox18;
	private: System::Windows::Forms::GroupBox^ groupBox2;
	private: System::Windows::Forms::Label^ label14;
	private: System::Windows::Forms::GroupBox^ groupBox3;
	private: System::Windows::Forms::GroupBox^ groupBox4;
	private: System::Windows::Forms::GroupBox^ groupBox5;
	private: System::Windows::Forms::TextBox^ textBox19;
	private: System::Windows::Forms::Button^ button7;
	private: System::Windows::Forms::TextBox^ textBox20;
	private: System::Windows::Forms::CheckBox^ checkBox4;
	private: System::Windows::Forms::CheckBox^ checkBox5;
	private: System::Windows::Forms::CheckBox^ checkBox6;
	private: System::Windows::Forms::GroupBox^ groupBox6;
	private: System::Windows::Forms::TextBox^ textBox22;
	private: System::Windows::Forms::TextBox^ textBox21;
	private: System::Windows::Forms::CheckBox^ checkBox7;
	private: System::Windows::Forms::GroupBox^ groupBox7;
	private: System::Windows::Forms::GroupBox^ groupBox8;
	private: System::Windows::Forms::FolderBrowserDialog^ folderBrowserDialog1;
	private: System::Windows::Forms::TextBox^ textBox23;
	private: System::Windows::Forms::GroupBox^ groupBox9;
	private: System::Windows::Forms::Button^ button8;
	private: System::Windows::Forms::GroupBox^ groupBox10;
	private: System::Windows::Forms::Label^ label15;
	private: System::Windows::Forms::TextBox^ textBox25;
	private: System::Windows::Forms::Label^ label17;
	private: System::Windows::Forms::TextBox^ textBox24;
	private: System::Windows::Forms::Label^ label16;
	private: System::Windows::Forms::RadioButton^ radioButton1;
	private: System::Windows::Forms::RadioButton^ radioButton2;
	private: System::Windows::Forms::TextBox^ textBox27;
	private: System::Windows::Forms::TextBox^ textBox26;
	private: System::Windows::Forms::Label^ label19;
	private: System::Windows::Forms::Label^ label18;
	private: System::Windows::Forms::CheckBox^ checkBox11;
	private: System::Windows::Forms::CheckBox^ checkBox10;
	private: System::Windows::Forms::CheckBox^ checkBox9;
	private: System::Windows::Forms::CheckBox^ checkBox8;
	private: System::Windows::Forms::CheckBox^ checkBox12;
	private: System::Windows::Forms::CheckBox^ checkBox13;
	private: System::Windows::Forms::CheckBox^ checkBox14;
	private: System::Windows::Forms::CheckBox^ checkBox15;
private: System::Windows::Forms::Button^ button9;
private: System::Windows::Forms::CheckBox^ checkBox18;
private: System::Windows::Forms::CheckBox^ checkBox17;
private: System::Windows::Forms::CheckBox^ checkBox16;
private: System::Windows::Forms::Button^ button10;
private: System::Windows::Forms::TextBox^ textBox28;
private: System::Windows::Forms::TextBox^ textBox29;
private: System::Windows::Forms::TextBox^ textBox30;
private: System::Windows::Forms::Button^ button11;
private: System::Windows::Forms::Label^ label20;
private: System::Windows::Forms::CheckBox^ checkBox19;
private: System::Windows::Forms::Button^ button12;
private: System::Windows::Forms::CheckBox^ checkBox20;
private: System::Windows::Forms::CheckBox^ checkBox21;
private: System::Windows::Forms::CheckBox^ checkBox22;
private: System::Windows::Forms::CheckBox^ checkBox23;
private: System::Windows::Forms::CheckBox^ checkBox24;
private: System::Windows::Forms::CheckBox^ checkBox25;
private: System::Windows::Forms::CheckBox^ checkBox26;
private: System::Windows::Forms::CheckBox^ checkBox27;
private: System::Windows::Forms::CheckBox^ checkBox28;
private: System::Windows::Forms::CheckBox^ checkBox29;
private: System::Windows::Forms::CheckBox^ checkBox30;
private: System::Windows::Forms::CheckBox^ checkBox31;
private: System::Windows::Forms::CheckBox^ checkBox32;
private: System::Windows::Forms::CheckBox^ checkBox33;
private: System::Windows::Forms::CheckBox^ checkBox34;
private: System::Windows::Forms::CheckBox^ checkBox35;
private: System::Windows::Forms::CheckBox^ checkBox36;
private: System::Windows::Forms::RadioButton^ radioButton3;
private: System::Windows::Forms::CheckBox^ checkBox37;
private: System::Windows::Forms::CheckBox^ checkBox38;
private: System::Windows::Forms::Label^ label21;
private: System::Windows::Forms::DataVisualization::Charting::Chart^ chart1;
private: System::Windows::Forms::Button^ button13;
private: System::Windows::Forms::ProgressBar^ progressBar2;
private: System::Windows::Forms::RadioButton^ radioButton5;
private: System::Windows::Forms::RadioButton^ radioButton4;
private: System::Windows::Forms::Button^ button14;
private: System::Windows::Forms::Button^ button15;

	protected:

	private:
		/// <summary>
		/// Required designer variable.
		/// </summary>
		System::ComponentModel::Container ^components;

#pragma region Windows Form Designer generated code
		/// <summary>
		/// Required method for Designer support - do not modify
		/// the contents of this method with the code editor.
		/// </summary>
		void InitializeComponent(void)
		{
			System::Windows::Forms::DataVisualization::Charting::ChartArea^ chartArea1 = (gcnew System::Windows::Forms::DataVisualization::Charting::ChartArea());
			System::Windows::Forms::DataVisualization::Charting::Legend^ legend1 = (gcnew System::Windows::Forms::DataVisualization::Charting::Legend());
			System::Windows::Forms::DataVisualization::Charting::Series^ series1 = (gcnew System::Windows::Forms::DataVisualization::Charting::Series());
			this->button1 = (gcnew System::Windows::Forms::Button());
			this->label1 = (gcnew System::Windows::Forms::Label());
			this->textBox1 = (gcnew System::Windows::Forms::TextBox());
			this->button2 = (gcnew System::Windows::Forms::Button());
			this->textBox2 = (gcnew System::Windows::Forms::TextBox());
			this->button3 = (gcnew System::Windows::Forms::Button());
			this->textBox3 = (gcnew System::Windows::Forms::TextBox());
			this->label2 = (gcnew System::Windows::Forms::Label());
			this->label3 = (gcnew System::Windows::Forms::Label());
			this->label4 = (gcnew System::Windows::Forms::Label());
			this->label5 = (gcnew System::Windows::Forms::Label());
			this->textBox4 = (gcnew System::Windows::Forms::TextBox());
			this->textBox5 = (gcnew System::Windows::Forms::TextBox());
			this->textBox6 = (gcnew System::Windows::Forms::TextBox());
			this->textBox7 = (gcnew System::Windows::Forms::TextBox());
			this->textBox8 = (gcnew System::Windows::Forms::TextBox());
			this->checkBox1 = (gcnew System::Windows::Forms::CheckBox());
			this->checkBox2 = (gcnew System::Windows::Forms::CheckBox());
			this->checkBox3 = (gcnew System::Windows::Forms::CheckBox());
			this->textBox9 = (gcnew System::Windows::Forms::TextBox());
			this->textBox10 = (gcnew System::Windows::Forms::TextBox());
			this->textBox11 = (gcnew System::Windows::Forms::TextBox());
			this->textBox12 = (gcnew System::Windows::Forms::TextBox());
			this->label6 = (gcnew System::Windows::Forms::Label());
			this->label7 = (gcnew System::Windows::Forms::Label());
			this->label8 = (gcnew System::Windows::Forms::Label());
			this->label9 = (gcnew System::Windows::Forms::Label());
			this->textBox13 = (gcnew System::Windows::Forms::TextBox());
			this->textBox14 = (gcnew System::Windows::Forms::TextBox());
			this->textBox15 = (gcnew System::Windows::Forms::TextBox());
			this->textBox16 = (gcnew System::Windows::Forms::TextBox());
			this->label10 = (gcnew System::Windows::Forms::Label());
			this->label11 = (gcnew System::Windows::Forms::Label());
			this->label12 = (gcnew System::Windows::Forms::Label());
			this->label13 = (gcnew System::Windows::Forms::Label());
			this->button4 = (gcnew System::Windows::Forms::Button());
			this->button5 = (gcnew System::Windows::Forms::Button());
			this->textBox17 = (gcnew System::Windows::Forms::TextBox());
			this->button6 = (gcnew System::Windows::Forms::Button());
			this->progressBar1 = (gcnew System::Windows::Forms::ProgressBar());
			this->groupBox1 = (gcnew System::Windows::Forms::GroupBox());
			this->checkBox4 = (gcnew System::Windows::Forms::CheckBox());
			this->textBox18 = (gcnew System::Windows::Forms::TextBox());
			this->groupBox2 = (gcnew System::Windows::Forms::GroupBox());
			this->checkBox12 = (gcnew System::Windows::Forms::CheckBox());
			this->checkBox18 = (gcnew System::Windows::Forms::CheckBox());
			this->checkBox13 = (gcnew System::Windows::Forms::CheckBox());
			this->checkBox17 = (gcnew System::Windows::Forms::CheckBox());
			this->checkBox14 = (gcnew System::Windows::Forms::CheckBox());
			this->checkBox15 = (gcnew System::Windows::Forms::CheckBox());
			this->checkBox16 = (gcnew System::Windows::Forms::CheckBox());
			this->checkBox11 = (gcnew System::Windows::Forms::CheckBox());
			this->checkBox10 = (gcnew System::Windows::Forms::CheckBox());
			this->checkBox9 = (gcnew System::Windows::Forms::CheckBox());
			this->checkBox8 = (gcnew System::Windows::Forms::CheckBox());
			this->label14 = (gcnew System::Windows::Forms::Label());
			this->groupBox3 = (gcnew System::Windows::Forms::GroupBox());
			this->radioButton5 = (gcnew System::Windows::Forms::RadioButton());
			this->radioButton4 = (gcnew System::Windows::Forms::RadioButton());
			this->checkBox38 = (gcnew System::Windows::Forms::CheckBox());
			this->checkBox6 = (gcnew System::Windows::Forms::CheckBox());
			this->groupBox4 = (gcnew System::Windows::Forms::GroupBox());
			this->chart1 = (gcnew System::Windows::Forms::DataVisualization::Charting::Chart());
			this->label21 = (gcnew System::Windows::Forms::Label());
			this->checkBox37 = (gcnew System::Windows::Forms::CheckBox());
			this->button11 = (gcnew System::Windows::Forms::Button());
			this->progressBar2 = (gcnew System::Windows::Forms::ProgressBar());
			this->button13 = (gcnew System::Windows::Forms::Button());
			this->groupBox5 = (gcnew System::Windows::Forms::GroupBox());
			this->checkBox5 = (gcnew System::Windows::Forms::CheckBox());
			this->textBox20 = (gcnew System::Windows::Forms::TextBox());
			this->button7 = (gcnew System::Windows::Forms::Button());
			this->textBox19 = (gcnew System::Windows::Forms::TextBox());
			this->groupBox6 = (gcnew System::Windows::Forms::GroupBox());
			this->checkBox7 = (gcnew System::Windows::Forms::CheckBox());
			this->textBox22 = (gcnew System::Windows::Forms::TextBox());
			this->textBox21 = (gcnew System::Windows::Forms::TextBox());
			this->groupBox7 = (gcnew System::Windows::Forms::GroupBox());
			this->button14 = (gcnew System::Windows::Forms::Button());
			this->radioButton3 = (gcnew System::Windows::Forms::RadioButton());
			this->checkBox28 = (gcnew System::Windows::Forms::CheckBox());
			this->textBox27 = (gcnew System::Windows::Forms::TextBox());
			this->checkBox29 = (gcnew System::Windows::Forms::CheckBox());
			this->textBox26 = (gcnew System::Windows::Forms::TextBox());
			this->checkBox30 = (gcnew System::Windows::Forms::CheckBox());
			this->label19 = (gcnew System::Windows::Forms::Label());
			this->checkBox31 = (gcnew System::Windows::Forms::CheckBox());
			this->label18 = (gcnew System::Windows::Forms::Label());
			this->checkBox32 = (gcnew System::Windows::Forms::CheckBox());
			this->radioButton2 = (gcnew System::Windows::Forms::RadioButton());
			this->checkBox33 = (gcnew System::Windows::Forms::CheckBox());
			this->radioButton1 = (gcnew System::Windows::Forms::RadioButton());
			this->checkBox34 = (gcnew System::Windows::Forms::CheckBox());
			this->textBox25 = (gcnew System::Windows::Forms::TextBox());
			this->checkBox35 = (gcnew System::Windows::Forms::CheckBox());
			this->label17 = (gcnew System::Windows::Forms::Label());
			this->textBox24 = (gcnew System::Windows::Forms::TextBox());
			this->label16 = (gcnew System::Windows::Forms::Label());
			this->groupBox8 = (gcnew System::Windows::Forms::GroupBox());
			this->checkBox36 = (gcnew System::Windows::Forms::CheckBox());
			this->textBox29 = (gcnew System::Windows::Forms::TextBox());
			this->button10 = (gcnew System::Windows::Forms::Button());
			this->textBox28 = (gcnew System::Windows::Forms::TextBox());
			this->folderBrowserDialog1 = (gcnew System::Windows::Forms::FolderBrowserDialog());
			this->textBox23 = (gcnew System::Windows::Forms::TextBox());
			this->groupBox9 = (gcnew System::Windows::Forms::GroupBox());
			this->label15 = (gcnew System::Windows::Forms::Label());
			this->button8 = (gcnew System::Windows::Forms::Button());
			this->groupBox10 = (gcnew System::Windows::Forms::GroupBox());
			this->checkBox20 = (gcnew System::Windows::Forms::CheckBox());
			this->button12 = (gcnew System::Windows::Forms::Button());
			this->checkBox21 = (gcnew System::Windows::Forms::CheckBox());
			this->checkBox19 = (gcnew System::Windows::Forms::CheckBox());
			this->checkBox22 = (gcnew System::Windows::Forms::CheckBox());
			this->checkBox23 = (gcnew System::Windows::Forms::CheckBox());
			this->label20 = (gcnew System::Windows::Forms::Label());
			this->checkBox24 = (gcnew System::Windows::Forms::CheckBox());
			this->textBox30 = (gcnew System::Windows::Forms::TextBox());
			this->checkBox25 = (gcnew System::Windows::Forms::CheckBox());
			this->checkBox26 = (gcnew System::Windows::Forms::CheckBox());
			this->checkBox27 = (gcnew System::Windows::Forms::CheckBox());
			this->button9 = (gcnew System::Windows::Forms::Button());
			this->button15 = (gcnew System::Windows::Forms::Button());
			this->groupBox1->SuspendLayout();
			this->groupBox2->SuspendLayout();
			this->groupBox3->SuspendLayout();
			this->groupBox4->SuspendLayout();
			(cli::safe_cast<System::ComponentModel::ISupportInitialize^>(this->chart1))->BeginInit();
			this->groupBox5->SuspendLayout();
			this->groupBox6->SuspendLayout();
			this->groupBox7->SuspendLayout();
			this->groupBox8->SuspendLayout();
			this->groupBox9->SuspendLayout();
			this->groupBox10->SuspendLayout();
			this->SuspendLayout();
			// 
			// button1
			// 
			this->button1->Location = System::Drawing::Point(256, 246);
			this->button1->Margin = System::Windows::Forms::Padding(3, 2, 3, 2);
			this->button1->Name = L"button1";
			this->button1->Size = System::Drawing::Size(125, 25);
			this->button1->TabIndex = 0;
			this->button1->Text = L"Magnetometer";
			this->button1->UseVisualStyleBackColor = true;
			this->button1->Click += gcnew System::EventHandler(this, &Form1::button1_Click);
			this->button1->KeyDown += gcnew System::Windows::Forms::KeyEventHandler(this, &Form1::Form1_KeyDown);
			// 
			// label1
			// 
			this->label1->AutoSize = true;
			this->label1->Location = System::Drawing::Point(42, 392);
			this->label1->Name = L"label1";
			this->label1->Size = System::Drawing::Size(28, 16);
			this->label1->TabIndex = 1;
			this->label1->Text = L"test";
			this->label1->Click += gcnew System::EventHandler(this, &Form1::label1_Click);
			// 
			// textBox1
			// 
			this->textBox1->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 8.25F, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox1->Location = System::Drawing::Point(43, 20);
			this->textBox1->Margin = System::Windows::Forms::Padding(3, 2, 3, 2);
			this->textBox1->Multiline = true;
			this->textBox1->Name = L"textBox1";
			this->textBox1->ScrollBars = System::Windows::Forms::ScrollBars::Both;
			this->textBox1->Size = System::Drawing::Size(350, 178);
			this->textBox1->TabIndex = 2;
			// 
			// button2
			// 
			this->button2->Location = System::Drawing::Point(3, 20);
			this->button2->Margin = System::Windows::Forms::Padding(3, 2, 3, 2);
			this->button2->Name = L"button2";
			this->button2->Size = System::Drawing::Size(167, 45);
			this->button2->TabIndex = 3;
			this->button2->TabStop = false;
			this->button2->Text = L"Search COM ports";
			this->button2->UseVisualStyleBackColor = true;
			this->button2->Click += gcnew System::EventHandler(this, &Form1::button2_Click);
			// 
			// textBox2
			// 
			this->textBox2->BackColor = System::Drawing::SystemColors::Window;
			this->textBox2->Location = System::Drawing::Point(43, 299);
			this->textBox2->Margin = System::Windows::Forms::Padding(3, 2, 3, 2);
			this->textBox2->Multiline = true;
			this->textBox2->Name = L"textBox2";
			this->textBox2->ReadOnly = true;
			this->textBox2->ScrollBars = System::Windows::Forms::ScrollBars::Both;
			this->textBox2->Size = System::Drawing::Size(350, 84);
			this->textBox2->TabIndex = 4;
			this->textBox2->KeyDown += gcnew System::Windows::Forms::KeyEventHandler(this, &Form1::Form1_KeyDown);
			this->textBox2->KeyPress += gcnew System::Windows::Forms::KeyPressEventHandler(this, &Form1::Form1_KeyPress);
			this->textBox2->KeyUp += gcnew System::Windows::Forms::KeyEventHandler(this, &Form1::Form1_KeyUp);
			// 
			// button3
			// 
			this->button3->Location = System::Drawing::Point(43, 246);
			this->button3->Margin = System::Windows::Forms::Padding(3, 2, 3, 2);
			this->button3->Name = L"button3";
			this->button3->Size = System::Drawing::Size(102, 26);
			this->button3->TabIndex = 5;
			this->button3->Text = L"Arduino";
			this->button3->UseVisualStyleBackColor = true;
			this->button3->Click += gcnew System::EventHandler(this, &Form1::button3_Click);
			// 
			// textBox3
			// 
			this->textBox3->BackColor = System::Drawing::SystemColors::Window;
			this->textBox3->Location = System::Drawing::Point(43, 212);
			this->textBox3->Margin = System::Windows::Forms::Padding(3, 2, 3, 2);
			this->textBox3->Multiline = true;
			this->textBox3->Name = L"textBox3";
			this->textBox3->ReadOnly = true;
			this->textBox3->ScrollBars = System::Windows::Forms::ScrollBars::Both;
			this->textBox3->Size = System::Drawing::Size(317, 28);
			this->textBox3->TabIndex = 6;
			// 
			// label2
			// 
			this->label2->AutoSize = true;
			this->label2->Location = System::Drawing::Point(161, 27);
			this->label2->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label2->Name = L"label2";
			this->label2->Size = System::Drawing::Size(22, 16);
			this->label2->TabIndex = 7;
			this->label2->Text = L"Bx";
			// 
			// label3
			// 
			this->label3->AutoSize = true;
			this->label3->Location = System::Drawing::Point(325, 27);
			this->label3->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label3->Name = L"label3";
			this->label3->Size = System::Drawing::Size(23, 16);
			this->label3->TabIndex = 8;
			this->label3->Text = L"By";
			// 
			// label4
			// 
			this->label4->AutoSize = true;
			this->label4->Location = System::Drawing::Point(499, 28);
			this->label4->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label4->Name = L"label4";
			this->label4->Size = System::Drawing::Size(22, 16);
			this->label4->TabIndex = 9;
			this->label4->Text = L"Bz";
			// 
			// label5
			// 
			this->label5->AutoSize = true;
			this->label5->Location = System::Drawing::Point(680, 30);
			this->label5->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label5->Name = L"label5";
			this->label5->Size = System::Drawing::Size(23, 16);
			this->label5->TabIndex = 10;
			this->label5->Text = L"Th";
			// 
			// textBox4
			// 
			this->textBox4->BackColor = System::Drawing::SystemColors::Info;
			this->textBox4->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox4->Location = System::Drawing::Point(195, 22);
			this->textBox4->Margin = System::Windows::Forms::Padding(4);
			this->textBox4->Name = L"textBox4";
			this->textBox4->ReadOnly = true;
			this->textBox4->Size = System::Drawing::Size(98, 26);
			this->textBox4->TabIndex = 11;
			this->textBox4->TabStop = false;
			// 
			// textBox5
			// 
			this->textBox5->BackColor = System::Drawing::SystemColors::Info;
			this->textBox5->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox5->Location = System::Drawing::Point(358, 23);
			this->textBox5->Margin = System::Windows::Forms::Padding(4);
			this->textBox5->Name = L"textBox5";
			this->textBox5->ReadOnly = true;
			this->textBox5->Size = System::Drawing::Size(108, 26);
			this->textBox5->TabIndex = 12;
			this->textBox5->TabStop = false;
			// 
			// textBox6
			// 
			this->textBox6->BackColor = System::Drawing::SystemColors::Info;
			this->textBox6->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox6->Location = System::Drawing::Point(532, 23);
			this->textBox6->Margin = System::Windows::Forms::Padding(4);
			this->textBox6->Name = L"textBox6";
			this->textBox6->ReadOnly = true;
			this->textBox6->Size = System::Drawing::Size(109, 26);
			this->textBox6->TabIndex = 13;
			this->textBox6->TabStop = false;
			// 
			// textBox7
			// 
			this->textBox7->BackColor = System::Drawing::SystemColors::Info;
			this->textBox7->Enabled = false;
			this->textBox7->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox7->Location = System::Drawing::Point(714, 24);
			this->textBox7->Margin = System::Windows::Forms::Padding(4);
			this->textBox7->Name = L"textBox7";
			this->textBox7->Size = System::Drawing::Size(111, 26);
			this->textBox7->TabIndex = 14;
			// 
			// textBox8
			// 
			this->textBox8->BackColor = System::Drawing::SystemColors::Info;
			this->textBox8->Location = System::Drawing::Point(176, 20);
			this->textBox8->Margin = System::Windows::Forms::Padding(3, 2, 3, 2);
			this->textBox8->Multiline = true;
			this->textBox8->Name = L"textBox8";
			this->textBox8->ReadOnly = true;
			this->textBox8->ScrollBars = System::Windows::Forms::ScrollBars::Both;
			this->textBox8->Size = System::Drawing::Size(128, 45);
			this->textBox8->TabIndex = 15;
			// 
			// checkBox1
			// 
			this->checkBox1->AutoSize = true;
			this->checkBox1->Enabled = false;
			this->checkBox1->Location = System::Drawing::Point(16, 27);
			this->checkBox1->Margin = System::Windows::Forms::Padding(4);
			this->checkBox1->Name = L"checkBox1";
			this->checkBox1->Size = System::Drawing::Size(56, 20);
			this->checkBox1->TabIndex = 16;
			this->checkBox1->Text = L"Front";
			this->checkBox1->UseVisualStyleBackColor = true;
			this->checkBox1->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox1_CheckedChanged);
			// 
			// checkBox2
			// 
			this->checkBox2->AutoSize = true;
			this->checkBox2->Enabled = false;
			this->checkBox2->Location = System::Drawing::Point(16, 72);
			this->checkBox2->Margin = System::Windows::Forms::Padding(4);
			this->checkBox2->Name = L"checkBox2";
			this->checkBox2->Size = System::Drawing::Size(52, 20);
			this->checkBox2->TabIndex = 17;
			this->checkBox2->Text = L"side";
			this->checkBox2->UseVisualStyleBackColor = true;
			this->checkBox2->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox2_CheckedChanged);
			// 
			// checkBox3
			// 
			this->checkBox3->AutoSize = true;
			this->checkBox3->Enabled = false;
			this->checkBox3->Location = System::Drawing::Point(16, 118);
			this->checkBox3->Margin = System::Windows::Forms::Padding(4);
			this->checkBox3->Name = L"checkBox3";
			this->checkBox3->Size = System::Drawing::Size(51, 20);
			this->checkBox3->TabIndex = 18;
			this->checkBox3->Text = L"Top";
			this->checkBox3->UseVisualStyleBackColor = true;
			this->checkBox3->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox3_CheckedChanged);
			// 
			// textBox9
			// 
			this->textBox9->BackColor = System::Drawing::SystemColors::Info;
			this->textBox9->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox9->Location = System::Drawing::Point(195, 70);
			this->textBox9->Margin = System::Windows::Forms::Padding(4);
			this->textBox9->Name = L"textBox9";
			this->textBox9->ReadOnly = true;
			this->textBox9->Size = System::Drawing::Size(98, 26);
			this->textBox9->TabIndex = 26;
			this->textBox9->TabStop = false;
			// 
			// textBox10
			// 
			this->textBox10->BackColor = System::Drawing::SystemColors::Info;
			this->textBox10->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox10->Location = System::Drawing::Point(358, 72);
			this->textBox10->Margin = System::Windows::Forms::Padding(4);
			this->textBox10->Name = L"textBox10";
			this->textBox10->ReadOnly = true;
			this->textBox10->Size = System::Drawing::Size(108, 26);
			this->textBox10->TabIndex = 25;
			this->textBox10->TabStop = false;
			// 
			// textBox11
			// 
			this->textBox11->BackColor = System::Drawing::SystemColors::Info;
			this->textBox11->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox11->Location = System::Drawing::Point(532, 73);
			this->textBox11->Margin = System::Windows::Forms::Padding(4);
			this->textBox11->Name = L"textBox11";
			this->textBox11->ReadOnly = true;
			this->textBox11->Size = System::Drawing::Size(109, 26);
			this->textBox11->TabIndex = 24;
			this->textBox11->TabStop = false;
			this->textBox11->TextChanged += gcnew System::EventHandler(this, &Form1::textBox11_TextChanged);
			// 
			// textBox12
			// 
			this->textBox12->BackColor = System::Drawing::SystemColors::Info;
			this->textBox12->Enabled = false;
			this->textBox12->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox12->Location = System::Drawing::Point(714, 74);
			this->textBox12->Margin = System::Windows::Forms::Padding(4);
			this->textBox12->Name = L"textBox12";
			this->textBox12->Size = System::Drawing::Size(111, 26);
			this->textBox12->TabIndex = 23;
			// 
			// label6
			// 
			this->label6->AutoSize = true;
			this->label6->Location = System::Drawing::Point(680, 78);
			this->label6->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label6->Name = L"label6";
			this->label6->Size = System::Drawing::Size(23, 16);
			this->label6->TabIndex = 22;
			this->label6->Text = L"Th";
			// 
			// label7
			// 
			this->label7->AutoSize = true;
			this->label7->Location = System::Drawing::Point(499, 76);
			this->label7->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label7->Name = L"label7";
			this->label7->Size = System::Drawing::Size(22, 16);
			this->label7->TabIndex = 21;
			this->label7->Text = L"Bz";
			// 
			// label8
			// 
			this->label8->AutoSize = true;
			this->label8->Location = System::Drawing::Point(325, 75);
			this->label8->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label8->Name = L"label8";
			this->label8->Size = System::Drawing::Size(23, 16);
			this->label8->TabIndex = 20;
			this->label8->Text = L"By";
			// 
			// label9
			// 
			this->label9->AutoSize = true;
			this->label9->Location = System::Drawing::Point(161, 74);
			this->label9->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label9->Name = L"label9";
			this->label9->Size = System::Drawing::Size(22, 16);
			this->label9->TabIndex = 19;
			this->label9->Text = L"Bx";
			// 
			// textBox13
			// 
			this->textBox13->BackColor = System::Drawing::SystemColors::Info;
			this->textBox13->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox13->Location = System::Drawing::Point(195, 119);
			this->textBox13->Margin = System::Windows::Forms::Padding(4);
			this->textBox13->Name = L"textBox13";
			this->textBox13->ReadOnly = true;
			this->textBox13->Size = System::Drawing::Size(98, 26);
			this->textBox13->TabIndex = 34;
			this->textBox13->TabStop = false;
			// 
			// textBox14
			// 
			this->textBox14->BackColor = System::Drawing::SystemColors::Info;
			this->textBox14->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox14->Location = System::Drawing::Point(358, 120);
			this->textBox14->Margin = System::Windows::Forms::Padding(4);
			this->textBox14->Name = L"textBox14";
			this->textBox14->ReadOnly = true;
			this->textBox14->Size = System::Drawing::Size(108, 26);
			this->textBox14->TabIndex = 33;
			this->textBox14->TabStop = false;
			// 
			// textBox15
			// 
			this->textBox15->BackColor = System::Drawing::SystemColors::Info;
			this->textBox15->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox15->Location = System::Drawing::Point(532, 120);
			this->textBox15->Margin = System::Windows::Forms::Padding(4);
			this->textBox15->Name = L"textBox15";
			this->textBox15->ReadOnly = true;
			this->textBox15->Size = System::Drawing::Size(109, 26);
			this->textBox15->TabIndex = 32;
			this->textBox15->TabStop = false;
			// 
			// textBox16
			// 
			this->textBox16->BackColor = System::Drawing::SystemColors::Info;
			this->textBox16->Enabled = false;
			this->textBox16->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox16->Location = System::Drawing::Point(713, 120);
			this->textBox16->Margin = System::Windows::Forms::Padding(4);
			this->textBox16->Name = L"textBox16";
			this->textBox16->Size = System::Drawing::Size(112, 26);
			this->textBox16->TabIndex = 31;
			// 
			// label10
			// 
			this->label10->AutoSize = true;
			this->label10->Location = System::Drawing::Point(679, 124);
			this->label10->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label10->Name = L"label10";
			this->label10->Size = System::Drawing::Size(23, 16);
			this->label10->TabIndex = 30;
			this->label10->Text = L"Th";
			// 
			// label11
			// 
			this->label11->AutoSize = true;
			this->label11->Location = System::Drawing::Point(499, 126);
			this->label11->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label11->Name = L"label11";
			this->label11->Size = System::Drawing::Size(22, 16);
			this->label11->TabIndex = 29;
			this->label11->Text = L"Bz";
			// 
			// label12
			// 
			this->label12->AutoSize = true;
			this->label12->Location = System::Drawing::Point(325, 122);
			this->label12->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label12->Name = L"label12";
			this->label12->Size = System::Drawing::Size(23, 16);
			this->label12->TabIndex = 28;
			this->label12->Text = L"By";
			// 
			// label13
			// 
			this->label13->AutoSize = true;
			this->label13->Location = System::Drawing::Point(161, 119);
			this->label13->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label13->Name = L"label13";
			this->label13->Size = System::Drawing::Size(22, 16);
			this->label13->TabIndex = 27;
			this->label13->Text = L"Bx";
			// 
			// button4
			// 
			this->button4->Location = System::Drawing::Point(8, 157);
			this->button4->Margin = System::Windows::Forms::Padding(4);
			this->button4->Name = L"button4";
			this->button4->Size = System::Drawing::Size(125, 82);
			this->button4->TabIndex = 35;
			this->button4->Text = L"Take Reading";
			this->button4->UseVisualStyleBackColor = true;
			this->button4->Click += gcnew System::EventHandler(this, &Form1::button4_Click);
			// 
			// button5
			// 
			this->button5->Location = System::Drawing::Point(702, 154);
			this->button5->Margin = System::Windows::Forms::Padding(4);
			this->button5->Name = L"button5";
			this->button5->Size = System::Drawing::Size(125, 81);
			this->button5->TabIndex = 36;
			this->button5->Text = L"Write Data to File";
			this->button5->UseVisualStyleBackColor = true;
			this->button5->Click += gcnew System::EventHandler(this, &Form1::button5_Click);
			// 
			// textBox17
			// 
			this->textBox17->BackColor = System::Drawing::SystemColors::GradientInactiveCaption;
			this->textBox17->Enabled = false;
			this->textBox17->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox17->Location = System::Drawing::Point(134, 48);
			this->textBox17->Margin = System::Windows::Forms::Padding(4);
			this->textBox17->Name = L"textBox17";
			this->textBox17->Size = System::Drawing::Size(163, 26);
			this->textBox17->TabIndex = 37;
			this->textBox17->TextChanged += gcnew System::EventHandler(this, &Form1::textBox17_TextChanged);
			// 
			// button6
			// 
			this->button6->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->button6->Location = System::Drawing::Point(3, 27);
			this->button6->Margin = System::Windows::Forms::Padding(4);
			this->button6->Name = L"button6";
			this->button6->Size = System::Drawing::Size(107, 61);
			this->button6->TabIndex = 38;
			this->button6->TabStop = false;
			this->button6->Text = L"Calibrate Arduino";
			this->button6->UseVisualStyleBackColor = true;
			this->button6->Click += gcnew System::EventHandler(this, &Form1::button6_Click);
			// 
			// progressBar1
			// 
			this->progressBar1->Location = System::Drawing::Point(6, 96);
			this->progressBar1->Margin = System::Windows::Forms::Padding(4);
			this->progressBar1->Name = L"progressBar1";
			this->progressBar1->Size = System::Drawing::Size(301, 36);
			this->progressBar1->Step = 6;
			this->progressBar1->TabIndex = 39;
			this->progressBar1->Click += gcnew System::EventHandler(this, &Form1::progressBar1_Click);
			// 
			// groupBox1
			// 
			this->groupBox1->Controls->Add(this->checkBox4);
			this->groupBox1->Controls->Add(this->textBox18);
			this->groupBox1->Controls->Add(this->button6);
			this->groupBox1->Controls->Add(this->progressBar1);
			this->groupBox1->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->groupBox1->Location = System::Drawing::Point(12, 207);
			this->groupBox1->Margin = System::Windows::Forms::Padding(4);
			this->groupBox1->Name = L"groupBox1";
			this->groupBox1->Padding = System::Windows::Forms::Padding(4);
			this->groupBox1->Size = System::Drawing::Size(317, 150);
			this->groupBox1->TabIndex = 40;
			this->groupBox1->TabStop = false;
			this->groupBox1->Text = L"Arduino Setup";
			// 
			// checkBox4
			// 
			this->checkBox4->AutoSize = true;
			this->checkBox4->Location = System::Drawing::Point(136, 64);
			this->checkBox4->Name = L"checkBox4";
			this->checkBox4->Size = System::Drawing::Size(159, 24);
			this->checkBox4->TabIndex = 41;
			this->checkBox4->TabStop = false;
			this->checkBox4->Text = L"Arduino Calibrated";
			this->checkBox4->UseVisualStyleBackColor = true;
			// 
			// textBox18
			// 
			this->textBox18->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox18->Location = System::Drawing::Point(136, 30);
			this->textBox18->Margin = System::Windows::Forms::Padding(4);
			this->textBox18->Name = L"textBox18";
			this->textBox18->Size = System::Drawing::Size(168, 26);
			this->textBox18->TabIndex = 40;
			this->textBox18->TabStop = false;
			this->textBox18->Text = L"COM8";
			this->textBox18->TextChanged += gcnew System::EventHandler(this, &Form1::textBox18_TextChanged);
			// 
			// groupBox2
			// 
			this->groupBox2->Controls->Add(this->checkBox12);
			this->groupBox2->Controls->Add(this->checkBox18);
			this->groupBox2->Controls->Add(this->checkBox13);
			this->groupBox2->Controls->Add(this->checkBox17);
			this->groupBox2->Controls->Add(this->checkBox14);
			this->groupBox2->Controls->Add(this->checkBox15);
			this->groupBox2->Controls->Add(this->checkBox16);
			this->groupBox2->Controls->Add(this->checkBox11);
			this->groupBox2->Controls->Add(this->button4);
			this->groupBox2->Controls->Add(this->checkBox10);
			this->groupBox2->Controls->Add(this->checkBox3);
			this->groupBox2->Controls->Add(this->checkBox9);
			this->groupBox2->Controls->Add(this->button5);
			this->groupBox2->Controls->Add(this->checkBox8);
			this->groupBox2->Controls->Add(this->textBox13);
			this->groupBox2->Controls->Add(this->label2);
			this->groupBox2->Controls->Add(this->textBox14);
			this->groupBox2->Controls->Add(this->label3);
			this->groupBox2->Controls->Add(this->textBox15);
			this->groupBox2->Controls->Add(this->label4);
			this->groupBox2->Controls->Add(this->textBox16);
			this->groupBox2->Controls->Add(this->label5);
			this->groupBox2->Controls->Add(this->label10);
			this->groupBox2->Controls->Add(this->textBox4);
			this->groupBox2->Controls->Add(this->label11);
			this->groupBox2->Controls->Add(this->textBox5);
			this->groupBox2->Controls->Add(this->label12);
			this->groupBox2->Controls->Add(this->textBox6);
			this->groupBox2->Controls->Add(this->label13);
			this->groupBox2->Controls->Add(this->textBox7);
			this->groupBox2->Controls->Add(this->textBox9);
			this->groupBox2->Controls->Add(this->checkBox1);
			this->groupBox2->Controls->Add(this->textBox10);
			this->groupBox2->Controls->Add(this->checkBox2);
			this->groupBox2->Controls->Add(this->textBox11);
			this->groupBox2->Controls->Add(this->label9);
			this->groupBox2->Controls->Add(this->textBox12);
			this->groupBox2->Controls->Add(this->label8);
			this->groupBox2->Controls->Add(this->label6);
			this->groupBox2->Controls->Add(this->label7);
			this->groupBox2->Location = System::Drawing::Point(338, 173);
			this->groupBox2->Margin = System::Windows::Forms::Padding(4);
			this->groupBox2->Name = L"groupBox2";
			this->groupBox2->Padding = System::Windows::Forms::Padding(4);
			this->groupBox2->Size = System::Drawing::Size(856, 248);
			this->groupBox2->TabIndex = 41;
			this->groupBox2->TabStop = false;
			this->groupBox2->Text = L"Teslameter Data";
			// 
			// checkBox12
			// 
			this->checkBox12->AutoSize = true;
			this->checkBox12->Enabled = false;
			this->checkBox12->Location = System::Drawing::Point(583, 199);
			this->checkBox12->Name = L"checkBox12";
			this->checkBox12->Size = System::Drawing::Size(70, 20);
			this->checkBox12->TabIndex = 56;
			this->checkBox12->Text = L"Slot 4-2";
			this->checkBox12->UseVisualStyleBackColor = true;
			this->checkBox12->Visible = false;
			this->checkBox12->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox12_CheckedChanged);
			// 
			// checkBox18
			// 
			this->checkBox18->AutoSize = true;
			this->checkBox18->Enabled = false;
			this->checkBox18->Location = System::Drawing::Point(83, 117);
			this->checkBox18->Name = L"checkBox18";
			this->checkBox18->Size = System::Drawing::Size(54, 20);
			this->checkBox18->TabIndex = 39;
			this->checkBox18->Text = L"read";
			this->checkBox18->UseVisualStyleBackColor = true;
			// 
			// checkBox13
			// 
			this->checkBox13->AutoSize = true;
			this->checkBox13->Enabled = false;
			this->checkBox13->Location = System::Drawing::Point(461, 199);
			this->checkBox13->Name = L"checkBox13";
			this->checkBox13->Size = System::Drawing::Size(70, 20);
			this->checkBox13->TabIndex = 55;
			this->checkBox13->Text = L"Slot 3-2";
			this->checkBox13->UseVisualStyleBackColor = true;
			this->checkBox13->Visible = false;
			this->checkBox13->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox13_CheckedChanged);
			// 
			// checkBox17
			// 
			this->checkBox17->AutoSize = true;
			this->checkBox17->Enabled = false;
			this->checkBox17->Location = System::Drawing::Point(84, 71);
			this->checkBox17->Name = L"checkBox17";
			this->checkBox17->Size = System::Drawing::Size(54, 20);
			this->checkBox17->TabIndex = 38;
			this->checkBox17->Text = L"read";
			this->checkBox17->UseVisualStyleBackColor = true;
			// 
			// checkBox14
			// 
			this->checkBox14->AutoSize = true;
			this->checkBox14->Enabled = false;
			this->checkBox14->Location = System::Drawing::Point(348, 197);
			this->checkBox14->Name = L"checkBox14";
			this->checkBox14->Size = System::Drawing::Size(70, 20);
			this->checkBox14->TabIndex = 54;
			this->checkBox14->Text = L"Slot 2-2";
			this->checkBox14->UseVisualStyleBackColor = true;
			this->checkBox14->Visible = false;
			this->checkBox14->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox14_CheckedChanged);
			// 
			// checkBox15
			// 
			this->checkBox15->AutoSize = true;
			this->checkBox15->Enabled = false;
			this->checkBox15->Location = System::Drawing::Point(235, 199);
			this->checkBox15->Name = L"checkBox15";
			this->checkBox15->Size = System::Drawing::Size(70, 20);
			this->checkBox15->TabIndex = 53;
			this->checkBox15->Text = L"Slot 1-2";
			this->checkBox15->UseVisualStyleBackColor = true;
			this->checkBox15->Visible = false;
			this->checkBox15->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox15_CheckedChanged);
			// 
			// checkBox16
			// 
			this->checkBox16->AutoSize = true;
			this->checkBox16->Enabled = false;
			this->checkBox16->Location = System::Drawing::Point(85, 27);
			this->checkBox16->Name = L"checkBox16";
			this->checkBox16->Size = System::Drawing::Size(54, 20);
			this->checkBox16->TabIndex = 37;
			this->checkBox16->Text = L"read";
			this->checkBox16->UseVisualStyleBackColor = true;
			// 
			// checkBox11
			// 
			this->checkBox11->AutoSize = true;
			this->checkBox11->Enabled = false;
			this->checkBox11->Location = System::Drawing::Point(542, 172);
			this->checkBox11->Name = L"checkBox11";
			this->checkBox11->Size = System::Drawing::Size(59, 20);
			this->checkBox11->TabIndex = 52;
			this->checkBox11->Text = L"Slot 4";
			this->checkBox11->UseVisualStyleBackColor = true;
			this->checkBox11->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox11_CheckedChanged);
			// 
			// checkBox10
			// 
			this->checkBox10->AutoSize = true;
			this->checkBox10->Enabled = false;
			this->checkBox10->Location = System::Drawing::Point(420, 172);
			this->checkBox10->Name = L"checkBox10";
			this->checkBox10->Size = System::Drawing::Size(59, 20);
			this->checkBox10->TabIndex = 51;
			this->checkBox10->Text = L"Slot 3";
			this->checkBox10->UseVisualStyleBackColor = true;
			this->checkBox10->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox10_CheckedChanged);
			// 
			// checkBox9
			// 
			this->checkBox9->AutoSize = true;
			this->checkBox9->Enabled = false;
			this->checkBox9->Location = System::Drawing::Point(307, 170);
			this->checkBox9->Name = L"checkBox9";
			this->checkBox9->Size = System::Drawing::Size(59, 20);
			this->checkBox9->TabIndex = 50;
			this->checkBox9->Text = L"Slot 2";
			this->checkBox9->UseVisualStyleBackColor = true;
			this->checkBox9->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox9_CheckedChanged);
			// 
			// checkBox8
			// 
			this->checkBox8->AutoSize = true;
			this->checkBox8->Enabled = false;
			this->checkBox8->Location = System::Drawing::Point(194, 172);
			this->checkBox8->Name = L"checkBox8";
			this->checkBox8->Size = System::Drawing::Size(59, 20);
			this->checkBox8->TabIndex = 49;
			this->checkBox8->Text = L"Slot 1";
			this->checkBox8->UseVisualStyleBackColor = true;
			this->checkBox8->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox8_CheckedChanged);
			// 
			// label14
			// 
			this->label14->AutoSize = true;
			this->label14->Location = System::Drawing::Point(11, 52);
			this->label14->Name = L"label14";
			this->label14->Size = System::Drawing::Size(105, 16);
			this->label14->TabIndex = 38;
			this->label14->Text = L"Sample number:";
			// 
			// groupBox3
			// 
			this->groupBox3->Controls->Add(this->radioButton5);
			this->groupBox3->Controls->Add(this->radioButton4);
			this->groupBox3->Controls->Add(this->checkBox38);
			this->groupBox3->Controls->Add(this->checkBox6);
			this->groupBox3->Controls->Add(this->button2);
			this->groupBox3->Controls->Add(this->textBox8);
			this->groupBox3->Location = System::Drawing::Point(12, 614);
			this->groupBox3->Name = L"groupBox3";
			this->groupBox3->Size = System::Drawing::Size(318, 124);
			this->groupBox3->TabIndex = 42;
			this->groupBox3->TabStop = false;
			this->groupBox3->Text = L"Toolkit";
			this->groupBox3->Enter += gcnew System::EventHandler(this, &Form1::groupBox3_Enter);
			// 
			// radioButton5
			// 
			this->radioButton5->AutoSize = true;
			this->radioButton5->Location = System::Drawing::Point(166, 96);
			this->radioButton5->Name = L"radioButton5";
			this->radioButton5->Size = System::Drawing::Size(116, 20);
			this->radioButton5->TabIndex = 48;
			this->radioButton5->Text = L"Dosimetry Only";
			this->radioButton5->UseVisualStyleBackColor = true;
			this->radioButton5->CheckedChanged += gcnew System::EventHandler(this, &Form1::radioButton5_CheckedChanged);
			// 
			// radioButton4
			// 
			this->radioButton4->AutoSize = true;
			this->radioButton4->Checked = true;
			this->radioButton4->Location = System::Drawing::Point(6, 96);
			this->radioButton4->Name = L"radioButton4";
			this->radioButton4->Size = System::Drawing::Size(102, 20);
			this->radioButton4->TabIndex = 47;
			this->radioButton4->TabStop = true;
			this->radioButton4->Text = L"Magnet Data";
			this->radioButton4->UseVisualStyleBackColor = true;
			// 
			// checkBox38
			// 
			this->checkBox38->AutoSize = true;
			this->checkBox38->Location = System::Drawing::Point(166, 70);
			this->checkBox38->Name = L"checkBox38";
			this->checkBox38->Size = System::Drawing::Size(141, 20);
			this->checkBox38->TabIndex = 46;
			this->checkBox38->Text = L"Manual Entry Mode";
			this->checkBox38->UseVisualStyleBackColor = true;
			this->checkBox38->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox38_CheckedChanged);
			// 
			// checkBox6
			// 
			this->checkBox6->AutoSize = true;
			this->checkBox6->Location = System::Drawing::Point(6, 69);
			this->checkBox6->Name = L"checkBox6";
			this->checkBox6->Size = System::Drawing::Size(105, 20);
			this->checkBox6->TabIndex = 45;
			this->checkBox6->Text = L"Debug Mode";
			this->checkBox6->UseVisualStyleBackColor = true;
			this->checkBox6->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox6_CheckedChanged);
			// 
			// groupBox4
			// 
			this->groupBox4->Controls->Add(this->chart1);
			this->groupBox4->Controls->Add(this->label21);
			this->groupBox4->Controls->Add(this->checkBox37);
			this->groupBox4->Controls->Add(this->textBox1);
			this->groupBox4->Controls->Add(this->button1);
			this->groupBox4->Controls->Add(this->textBox3);
			this->groupBox4->Controls->Add(this->textBox2);
			this->groupBox4->Controls->Add(this->label1);
			this->groupBox4->Controls->Add(this->button3);
			this->groupBox4->Controls->Add(this->button11);
			this->groupBox4->Location = System::Drawing::Point(1256, 14);
			this->groupBox4->Name = L"groupBox4";
			this->groupBox4->Size = System::Drawing::Size(399, 678);
			this->groupBox4->TabIndex = 43;
			this->groupBox4->TabStop = false;
			this->groupBox4->Text = L"Debugging Tools";
			this->groupBox4->Visible = false;
			// 
			// chart1
			// 
			chartArea1->CursorX->IsUserSelectionEnabled = true;
			chartArea1->CursorY->IsUserSelectionEnabled = true;
			chartArea1->Name = L"ChartArea1";
			this->chart1->ChartAreas->Add(chartArea1);
			legend1->Enabled = false;
			legend1->Name = L"Legend1";
			this->chart1->Legends->Add(legend1);
			this->chart1->Location = System::Drawing::Point(42, 426);
			this->chart1->Name = L"chart1";
			series1->ChartArea = L"ChartArea1";
			series1->ChartType = System::Windows::Forms::DataVisualization::Charting::SeriesChartType::Line;
			series1->Legend = L"Legend1";
			series1->Name = L"Series1";
			this->chart1->Series->Add(series1);
			this->chart1->Size = System::Drawing::Size(351, 189);
			this->chart1->TabIndex = 54;
			this->chart1->Text = L"chart1";
			// 
			// label21
			// 
			this->label21->AutoSize = true;
			this->label21->Location = System::Drawing::Point(60, 646);
			this->label21->Name = L"label21";
			this->label21->Size = System::Drawing::Size(10, 16);
			this->label21->TabIndex = 53;
			this->label21->Text = L" ";
			// 
			// checkBox37
			// 
			this->checkBox37->AutoSize = true;
			this->checkBox37->Enabled = false;
			this->checkBox37->Location = System::Drawing::Point(42, 622);
			this->checkBox37->Margin = System::Windows::Forms::Padding(4);
			this->checkBox37->Name = L"checkBox37";
			this->checkBox37->Size = System::Drawing::Size(266, 20);
			this->checkBox37->TabIndex = 52;
			this->checkBox37->Text = L"Someting has gone horribly wrong mode";
			this->checkBox37->UseVisualStyleBackColor = true;
			this->checkBox37->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox37_CheckedChanged);
			// 
			// button11
			// 
			this->button11->Location = System::Drawing::Point(145, 247);
			this->button11->Name = L"button11";
			this->button11->Size = System::Drawing::Size(108, 25);
			this->button11->TabIndex = 0;
			this->button11->Text = L"Take Reading";
			this->button11->UseVisualStyleBackColor = true;
			this->button11->Click += gcnew System::EventHandler(this, &Form1::button11_Click);
			// 
			// progressBar2
			// 
			this->progressBar2->Location = System::Drawing::Point(282, 156);
			this->progressBar2->Maximum = 59;
			this->progressBar2->Name = L"progressBar2";
			this->progressBar2->Size = System::Drawing::Size(347, 23);
			this->progressBar2->TabIndex = 56;
			// 
			// button13
			// 
			this->button13->Location = System::Drawing::Point(17, 33);
			this->button13->Name = L"button13";
			this->button13->Size = System::Drawing::Size(116, 39);
			this->button13->TabIndex = 55;
			this->button13->Text = L"Helmholtz";
			this->button13->UseVisualStyleBackColor = true;
			this->button13->Click += gcnew System::EventHandler(this, &Form1::button13_Click);
			// 
			// groupBox5
			// 
			this->groupBox5->Controls->Add(this->checkBox5);
			this->groupBox5->Controls->Add(this->textBox20);
			this->groupBox5->Controls->Add(this->button7);
			this->groupBox5->Controls->Add(this->textBox19);
			this->groupBox5->Location = System::Drawing::Point(12, 361);
			this->groupBox5->Name = L"groupBox5";
			this->groupBox5->Size = System::Drawing::Size(317, 130);
			this->groupBox5->TabIndex = 44;
			this->groupBox5->TabStop = false;
			this->groupBox5->Text = L"Teslameter Setup";
			// 
			// checkBox5
			// 
			this->checkBox5->AutoSize = true;
			this->checkBox5->Location = System::Drawing::Point(139, 53);
			this->checkBox5->Name = L"checkBox5";
			this->checkBox5->Size = System::Drawing::Size(163, 20);
			this->checkBox5->TabIndex = 3;
			this->checkBox5->TabStop = false;
			this->checkBox5->Text = L"Teslameter Connected";
			this->checkBox5->UseVisualStyleBackColor = true;
			// 
			// textBox20
			// 
			this->textBox20->BackColor = System::Drawing::SystemColors::Info;
			this->textBox20->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox20->Location = System::Drawing::Point(9, 88);
			this->textBox20->Name = L"textBox20";
			this->textBox20->ReadOnly = true;
			this->textBox20->Size = System::Drawing::Size(298, 26);
			this->textBox20->TabIndex = 2;
			// 
			// button7
			// 
			this->button7->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->button7->Location = System::Drawing::Point(9, 22);
			this->button7->Name = L"button7";
			this->button7->Size = System::Drawing::Size(124, 60);
			this->button7->TabIndex = 1;
			this->button7->TabStop = false;
			this->button7->Text = L"Test Teslameter";
			this->button7->UseVisualStyleBackColor = true;
			this->button7->Click += gcnew System::EventHandler(this, &Form1::button7_Click);
			// 
			// textBox19
			// 
			this->textBox19->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox19->Location = System::Drawing::Point(139, 21);
			this->textBox19->Name = L"textBox19";
			this->textBox19->Size = System::Drawing::Size(165, 26);
			this->textBox19->TabIndex = 0;
			this->textBox19->TabStop = false;
			this->textBox19->Text = L"COM6";
			// 
			// groupBox6
			// 
			this->groupBox6->Controls->Add(this->checkBox7);
			this->groupBox6->Controls->Add(this->textBox22);
			this->groupBox6->Controls->Add(this->textBox21);
			this->groupBox6->Location = System::Drawing::Point(12, 110);
			this->groupBox6->Name = L"groupBox6";
			this->groupBox6->Size = System::Drawing::Size(317, 95);
			this->groupBox6->TabIndex = 45;
			this->groupBox6->TabStop = false;
			this->groupBox6->Text = L"Barcode Setup";
			// 
			// checkBox7
			// 
			this->checkBox7->AutoSize = true;
			this->checkBox7->Enabled = false;
			this->checkBox7->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->checkBox7->ForeColor = System::Drawing::SystemColors::Desktop;
			this->checkBox7->Location = System::Drawing::Point(9, 62);
			this->checkBox7->Name = L"checkBox7";
			this->checkBox7->Size = System::Drawing::Size(232, 24);
			this->checkBox7->TabIndex = 2;
			this->checkBox7->Text = L"Barcode Reader Functioning";
			this->checkBox7->UseVisualStyleBackColor = true;
			// 
			// textBox22
			// 
			this->textBox22->Enabled = false;
			this->textBox22->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox22->Location = System::Drawing::Point(169, 27);
			this->textBox22->Name = L"textBox22";
			this->textBox22->Size = System::Drawing::Size(135, 26);
			this->textBox22->TabIndex = 1;
			this->textBox22->TextChanged += gcnew System::EventHandler(this, &Form1::textBox22_TextChanged);
			// 
			// textBox21
			// 
			this->textBox21->BackColor = System::Drawing::SystemColors::Info;
			this->textBox21->Enabled = false;
			this->textBox21->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox21->Location = System::Drawing::Point(9, 27);
			this->textBox21->Name = L"textBox21";
			this->textBox21->Size = System::Drawing::Size(137, 26);
			this->textBox21->TabIndex = 0;
			this->textBox21->Text = L"ABCabc123";
			// 
			// groupBox7
			// 
			this->groupBox7->Controls->Add(this->button14);
			this->groupBox7->Controls->Add(this->radioButton3);
			this->groupBox7->Controls->Add(this->checkBox28);
			this->groupBox7->Controls->Add(this->textBox27);
			this->groupBox7->Controls->Add(this->checkBox29);
			this->groupBox7->Controls->Add(this->textBox26);
			this->groupBox7->Controls->Add(this->checkBox30);
			this->groupBox7->Controls->Add(this->label19);
			this->groupBox7->Controls->Add(this->checkBox31);
			this->groupBox7->Controls->Add(this->label18);
			this->groupBox7->Controls->Add(this->checkBox32);
			this->groupBox7->Controls->Add(this->radioButton2);
			this->groupBox7->Controls->Add(this->checkBox33);
			this->groupBox7->Controls->Add(this->radioButton1);
			this->groupBox7->Controls->Add(this->checkBox34);
			this->groupBox7->Controls->Add(this->textBox25);
			this->groupBox7->Controls->Add(this->checkBox35);
			this->groupBox7->Controls->Add(this->label17);
			this->groupBox7->Controls->Add(this->textBox24);
			this->groupBox7->Controls->Add(this->label16);
			this->groupBox7->Controls->Add(this->label14);
			this->groupBox7->Controls->Add(this->textBox17);
			this->groupBox7->Location = System::Drawing::Point(338, 13);
			this->groupBox7->Name = L"groupBox7";
			this->groupBox7->Size = System::Drawing::Size(856, 153);
			this->groupBox7->TabIndex = 46;
			this->groupBox7->TabStop = false;
			this->groupBox7->Text = L"Plate Info";
			// 
			// button14
			// 
			this->button14->Location = System::Drawing::Point(730, 22);
			this->button14->Name = L"button14";
			this->button14->Size = System::Drawing::Size(97, 108);
			this->button14->TabIndex = 74;
			this->button14->Text = L"Log Dosimetry";
			this->button14->UseVisualStyleBackColor = true;
			this->button14->Visible = false;
			this->button14->Click += gcnew System::EventHandler(this, &Form1::button14_Click);
			// 
			// radioButton3
			// 
			this->radioButton3->AutoSize = true;
			this->radioButton3->Enabled = false;
			this->radioButton3->Location = System::Drawing::Point(579, 54);
			this->radioButton3->Name = L"radioButton3";
			this->radioButton3->Size = System::Drawing::Size(129, 20);
			this->radioButton3->TabIndex = 73;
			this->radioButton3->TabStop = true;
			this->radioButton3->Text = L"Assembly Holder";
			this->radioButton3->UseVisualStyleBackColor = true;
			this->radioButton3->CheckedChanged += gcnew System::EventHandler(this, &Form1::radioButton3_CheckedChanged);
			// 
			// checkBox28
			// 
			this->checkBox28->AutoSize = true;
			this->checkBox28->Enabled = false;
			this->checkBox28->Location = System::Drawing::Point(628, 113);
			this->checkBox28->Name = L"checkBox28";
			this->checkBox28->Size = System::Drawing::Size(70, 20);
			this->checkBox28->TabIndex = 72;
			this->checkBox28->Text = L"Slot 4-2";
			this->checkBox28->UseVisualStyleBackColor = true;
			this->checkBox28->Visible = false;
			this->checkBox28->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox28_CheckedChanged);
			// 
			// textBox27
			// 
			this->textBox27->BackColor = System::Drawing::SystemColors::GradientInactiveCaption;
			this->textBox27->Enabled = false;
			this->textBox27->Location = System::Drawing::Point(109, 116);
			this->textBox27->Name = L"textBox27";
			this->textBox27->Size = System::Drawing::Size(100, 22);
			this->textBox27->TabIndex = 48;
			// 
			// checkBox29
			// 
			this->checkBox29->AutoSize = true;
			this->checkBox29->Enabled = false;
			this->checkBox29->Location = System::Drawing::Point(506, 114);
			this->checkBox29->Name = L"checkBox29";
			this->checkBox29->Size = System::Drawing::Size(70, 20);
			this->checkBox29->TabIndex = 71;
			this->checkBox29->Text = L"Slot 3-2";
			this->checkBox29->UseVisualStyleBackColor = true;
			this->checkBox29->Visible = false;
			this->checkBox29->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox29_CheckedChanged);
			// 
			// textBox26
			// 
			this->textBox26->BackColor = System::Drawing::SystemColors::GradientInactiveCaption;
			this->textBox26->Enabled = false;
			this->textBox26->Location = System::Drawing::Point(109, 87);
			this->textBox26->Name = L"textBox26";
			this->textBox26->Size = System::Drawing::Size(100, 22);
			this->textBox26->TabIndex = 47;
			// 
			// checkBox30
			// 
			this->checkBox30->AutoSize = true;
			this->checkBox30->Enabled = false;
			this->checkBox30->Location = System::Drawing::Point(393, 115);
			this->checkBox30->Name = L"checkBox30";
			this->checkBox30->Size = System::Drawing::Size(70, 20);
			this->checkBox30->TabIndex = 70;
			this->checkBox30->Text = L"Slot 2-2";
			this->checkBox30->UseVisualStyleBackColor = true;
			this->checkBox30->Visible = false;
			this->checkBox30->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox30_CheckedChanged);
			// 
			// label19
			// 
			this->label19->AutoSize = true;
			this->label19->Location = System::Drawing::Point(13, 114);
			this->label19->Name = L"label19";
			this->label19->Size = System::Drawing::Size(84, 16);
			this->label19->TabIndex = 46;
			this->label19->Text = L"Slot  Number";
			// 
			// checkBox31
			// 
			this->checkBox31->AutoSize = true;
			this->checkBox31->Enabled = false;
			this->checkBox31->Location = System::Drawing::Point(280, 115);
			this->checkBox31->Name = L"checkBox31";
			this->checkBox31->Size = System::Drawing::Size(70, 20);
			this->checkBox31->TabIndex = 69;
			this->checkBox31->Text = L"Slot 1-2";
			this->checkBox31->UseVisualStyleBackColor = true;
			this->checkBox31->Visible = false;
			this->checkBox31->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox31_CheckedChanged);
			// 
			// label18
			// 
			this->label18->AutoSize = true;
			this->label18->Location = System::Drawing::Point(13, 87);
			this->label18->Name = L"label18";
			this->label18->Size = System::Drawing::Size(89, 16);
			this->label18->TabIndex = 45;
			this->label18->Text = L"Plate Number";
			// 
			// checkBox32
			// 
			this->checkBox32->AutoSize = true;
			this->checkBox32->Enabled = false;
			this->checkBox32->Location = System::Drawing::Point(586, 89);
			this->checkBox32->Name = L"checkBox32";
			this->checkBox32->Size = System::Drawing::Size(59, 20);
			this->checkBox32->TabIndex = 68;
			this->checkBox32->Text = L"Slot 4";
			this->checkBox32->UseVisualStyleBackColor = true;
			this->checkBox32->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox32_CheckedChanged);
			// 
			// radioButton2
			// 
			this->radioButton2->AutoSize = true;
			this->radioButton2->Enabled = false;
			this->radioButton2->Location = System::Drawing::Point(435, 52);
			this->radioButton2->Name = L"radioButton2";
			this->radioButton2->Size = System::Drawing::Size(135, 20);
			this->radioButton2->TabIndex = 44;
			this->radioButton2->TabStop = true;
			this->radioButton2->Text = L"Assembly Sample";
			this->radioButton2->UseVisualStyleBackColor = true;
			this->radioButton2->CheckedChanged += gcnew System::EventHandler(this, &Form1::radioButton2_CheckedChanged);
			// 
			// checkBox33
			// 
			this->checkBox33->AutoSize = true;
			this->checkBox33->Enabled = false;
			this->checkBox33->Location = System::Drawing::Point(464, 89);
			this->checkBox33->Name = L"checkBox33";
			this->checkBox33->Size = System::Drawing::Size(59, 20);
			this->checkBox33->TabIndex = 67;
			this->checkBox33->Text = L"Slot 3";
			this->checkBox33->UseVisualStyleBackColor = true;
			this->checkBox33->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox33_CheckedChanged);
			// 
			// radioButton1
			// 
			this->radioButton1->AutoSize = true;
			this->radioButton1->Enabled = false;
			this->radioButton1->Location = System::Drawing::Point(316, 52);
			this->radioButton1->Name = L"radioButton1";
			this->radioButton1->Size = System::Drawing::Size(113, 20);
			this->radioButton1->TabIndex = 43;
			this->radioButton1->TabStop = true;
			this->radioButton1->Text = L"Single Sample";
			this->radioButton1->UseVisualStyleBackColor = true;
			// 
			// checkBox34
			// 
			this->checkBox34->AutoSize = true;
			this->checkBox34->Enabled = false;
			this->checkBox34->Location = System::Drawing::Point(351, 87);
			this->checkBox34->Name = L"checkBox34";
			this->checkBox34->Size = System::Drawing::Size(59, 20);
			this->checkBox34->TabIndex = 66;
			this->checkBox34->Text = L"Slot 2";
			this->checkBox34->UseVisualStyleBackColor = true;
			this->checkBox34->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox34_CheckedChanged);
			// 
			// textBox25
			// 
			this->textBox25->BackColor = System::Drawing::SystemColors::GradientInactiveCaption;
			this->textBox25->Enabled = false;
			this->textBox25->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox25->Location = System::Drawing::Point(550, 20);
			this->textBox25->Name = L"textBox25";
			this->textBox25->Size = System::Drawing::Size(164, 26);
			this->textBox25->TabIndex = 42;
			// 
			// checkBox35
			// 
			this->checkBox35->AutoSize = true;
			this->checkBox35->Enabled = false;
			this->checkBox35->Location = System::Drawing::Point(238, 89);
			this->checkBox35->Name = L"checkBox35";
			this->checkBox35->Size = System::Drawing::Size(59, 20);
			this->checkBox35->TabIndex = 65;
			this->checkBox35->Text = L"Slot 1";
			this->checkBox35->UseVisualStyleBackColor = true;
			this->checkBox35->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox35_CheckedChanged);
			// 
			// label17
			// 
			this->label17->AutoSize = true;
			this->label17->Location = System::Drawing::Point(424, 22);
			this->label17->Name = L"label17";
			this->label17->Size = System::Drawing::Size(122, 16);
			this->label17->TabIndex = 41;
			this->label17->Text = L"Rod Tube Number:";
			// 
			// textBox24
			// 
			this->textBox24->BackColor = System::Drawing::SystemColors::GradientInactiveCaption;
			this->textBox24->Enabled = false;
			this->textBox24->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox24->Location = System::Drawing::Point(133, 19);
			this->textBox24->Name = L"textBox24";
			this->textBox24->Size = System::Drawing::Size(164, 26);
			this->textBox24->TabIndex = 40;
			this->textBox24->TextChanged += gcnew System::EventHandler(this, &Form1::textBox24_TextChanged);
			// 
			// label16
			// 
			this->label16->AutoSize = true;
			this->label16->Location = System::Drawing::Point(10, 22);
			this->label16->Name = L"label16";
			this->label16->Size = System::Drawing::Size(123, 16);
			this->label16->TabIndex = 39;
			this->label16->Text = L"Dosimeter Number:";
			// 
			// groupBox8
			// 
			this->groupBox8->Controls->Add(this->checkBox36);
			this->groupBox8->Controls->Add(this->textBox29);
			this->groupBox8->Controls->Add(this->button10);
			this->groupBox8->Controls->Add(this->textBox28);
			this->groupBox8->Location = System::Drawing::Point(12, 496);
			this->groupBox8->Name = L"groupBox8";
			this->groupBox8->Size = System::Drawing::Size(319, 112);
			this->groupBox8->TabIndex = 47;
			this->groupBox8->TabStop = false;
			this->groupBox8->Text = L"Helmholtz Coil Setup";
			// 
			// checkBox36
			// 
			this->checkBox36->AutoSize = true;
			this->checkBox36->Location = System::Drawing::Point(139, 46);
			this->checkBox36->Name = L"checkBox36";
			this->checkBox36->Size = System::Drawing::Size(120, 20);
			this->checkBox36->TabIndex = 3;
			this->checkBox36->Text = L"Use Helmholtz\?";
			this->checkBox36->UseVisualStyleBackColor = true;
			// 
			// textBox29
			// 
			this->textBox29->BackColor = System::Drawing::SystemColors::Info;
			this->textBox29->Enabled = false;
			this->textBox29->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox29->Location = System::Drawing::Point(11, 69);
			this->textBox29->Name = L"textBox29";
			this->textBox29->Size = System::Drawing::Size(296, 26);
			this->textBox29->TabIndex = 2;
			// 
			// button10
			// 
			this->button10->Location = System::Drawing::Point(11, 22);
			this->button10->Name = L"button10";
			this->button10->Size = System::Drawing::Size(122, 40);
			this->button10->TabIndex = 1;
			this->button10->Text = L"Test Helmholtz Coil";
			this->button10->UseVisualStyleBackColor = true;
			this->button10->Click += gcnew System::EventHandler(this, &Form1::button10_Click);
			// 
			// textBox28
			// 
			this->textBox28->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox28->Location = System::Drawing::Point(136, 12);
			this->textBox28->Name = L"textBox28";
			this->textBox28->Size = System::Drawing::Size(166, 26);
			this->textBox28->TabIndex = 0;
			this->textBox28->Text = L"COM7";
			// 
			// textBox23
			// 
			this->textBox23->Location = System::Drawing::Point(11, 59);
			this->textBox23->Name = L"textBox23";
			this->textBox23->Size = System::Drawing::Size(300, 22);
			this->textBox23->TabIndex = 48;
			this->textBox23->Text = L"C:\\Users\\Public\\Documents\\";
			// 
			// groupBox9
			// 
			this->groupBox9->Controls->Add(this->label15);
			this->groupBox9->Controls->Add(this->button8);
			this->groupBox9->Controls->Add(this->textBox23);
			this->groupBox9->Location = System::Drawing::Point(12, 13);
			this->groupBox9->Name = L"groupBox9";
			this->groupBox9->Size = System::Drawing::Size(317, 91);
			this->groupBox9->TabIndex = 49;
			this->groupBox9->TabStop = false;
			this->groupBox9->Text = L"Output Folder";
			// 
			// label15
			// 
			this->label15->AutoSize = true;
			this->label15->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 9.75F, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->label15->Location = System::Drawing::Point(130, 29);
			this->label15->Name = L"label15";
			this->label15->Size = System::Drawing::Size(160, 16);
			this->label15->TabIndex = 49;
			this->label15->Text = L"Blank saves to .exe folder";
			// 
			// button8
			// 
			this->button8->Location = System::Drawing::Point(9, 22);
			this->button8->Name = L"button8";
			this->button8->Size = System::Drawing::Size(115, 31);
			this->button8->TabIndex = 1;
			this->button8->Text = L"Select Output";
			this->button8->UseVisualStyleBackColor = true;
			this->button8->Click += gcnew System::EventHandler(this, &Form1::button8_Click);
			// 
			// groupBox10
			// 
			this->groupBox10->Controls->Add(this->button13);
			this->groupBox10->Controls->Add(this->progressBar2);
			this->groupBox10->Controls->Add(this->checkBox20);
			this->groupBox10->Controls->Add(this->button12);
			this->groupBox10->Controls->Add(this->checkBox21);
			this->groupBox10->Controls->Add(this->checkBox19);
			this->groupBox10->Controls->Add(this->checkBox22);
			this->groupBox10->Controls->Add(this->checkBox23);
			this->groupBox10->Controls->Add(this->label20);
			this->groupBox10->Controls->Add(this->checkBox24);
			this->groupBox10->Controls->Add(this->textBox30);
			this->groupBox10->Controls->Add(this->checkBox25);
			this->groupBox10->Controls->Add(this->checkBox26);
			this->groupBox10->Controls->Add(this->checkBox27);
			this->groupBox10->Location = System::Drawing::Point(338, 429);
			this->groupBox10->Name = L"groupBox10";
			this->groupBox10->Size = System::Drawing::Size(856, 200);
			this->groupBox10->TabIndex = 50;
			this->groupBox10->TabStop = false;
			this->groupBox10->Text = L"Helmholtz coil data";
			// 
			// checkBox20
			// 
			this->checkBox20->AutoSize = true;
			this->checkBox20->Enabled = false;
			this->checkBox20->Location = System::Drawing::Point(600, 109);
			this->checkBox20->Name = L"checkBox20";
			this->checkBox20->Size = System::Drawing::Size(70, 20);
			this->checkBox20->TabIndex = 64;
			this->checkBox20->Text = L"Slot 4-2";
			this->checkBox20->UseVisualStyleBackColor = true;
			this->checkBox20->Visible = false;
			this->checkBox20->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox20_CheckedChanged);
			// 
			// button12
			// 
			this->button12->Location = System::Drawing::Point(659, 22);
			this->button12->Name = L"button12";
			this->button12->Size = System::Drawing::Size(167, 50);
			this->button12->TabIndex = 4;
			this->button12->Text = L"Write Data to FIle";
			this->button12->UseVisualStyleBackColor = true;
			this->button12->Click += gcnew System::EventHandler(this, &Form1::button12_Click);
			// 
			// checkBox21
			// 
			this->checkBox21->AutoSize = true;
			this->checkBox21->Enabled = false;
			this->checkBox21->Location = System::Drawing::Point(477, 109);
			this->checkBox21->Name = L"checkBox21";
			this->checkBox21->Size = System::Drawing::Size(70, 20);
			this->checkBox21->TabIndex = 63;
			this->checkBox21->Text = L"Slot 3-2";
			this->checkBox21->UseVisualStyleBackColor = true;
			this->checkBox21->Visible = false;
			this->checkBox21->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox21_CheckedChanged);
			// 
			// checkBox19
			// 
			this->checkBox19->AutoSize = true;
			this->checkBox19->Enabled = false;
			this->checkBox19->Location = System::Drawing::Point(147, 39);
			this->checkBox19->Name = L"checkBox19";
			this->checkBox19->Size = System::Drawing::Size(54, 20);
			this->checkBox19->TabIndex = 3;
			this->checkBox19->Text = L"read";
			this->checkBox19->UseVisualStyleBackColor = true;
			// 
			// checkBox22
			// 
			this->checkBox22->AutoSize = true;
			this->checkBox22->Enabled = false;
			this->checkBox22->Location = System::Drawing::Point(364, 109);
			this->checkBox22->Name = L"checkBox22";
			this->checkBox22->Size = System::Drawing::Size(70, 20);
			this->checkBox22->TabIndex = 62;
			this->checkBox22->Text = L"Slot 2-2";
			this->checkBox22->UseVisualStyleBackColor = true;
			this->checkBox22->Visible = false;
			this->checkBox22->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox22_CheckedChanged);
			// 
			// checkBox23
			// 
			this->checkBox23->AutoSize = true;
			this->checkBox23->Enabled = false;
			this->checkBox23->Location = System::Drawing::Point(251, 109);
			this->checkBox23->Name = L"checkBox23";
			this->checkBox23->Size = System::Drawing::Size(70, 20);
			this->checkBox23->TabIndex = 61;
			this->checkBox23->Text = L"Slot 1-2";
			this->checkBox23->UseVisualStyleBackColor = true;
			this->checkBox23->Visible = false;
			this->checkBox23->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox23_CheckedChanged);
			// 
			// label20
			// 
			this->label20->AutoSize = true;
			this->label20->Location = System::Drawing::Point(215, 39);
			this->label20->Name = L"label20";
			this->label20->Size = System::Drawing::Size(86, 16);
			this->label20->TabIndex = 2;
			this->label20->Text = L"Flux Reading";
			// 
			// checkBox24
			// 
			this->checkBox24->AutoSize = true;
			this->checkBox24->Enabled = false;
			this->checkBox24->Location = System::Drawing::Point(558, 84);
			this->checkBox24->Name = L"checkBox24";
			this->checkBox24->Size = System::Drawing::Size(59, 20);
			this->checkBox24->TabIndex = 60;
			this->checkBox24->Text = L"Slot 4";
			this->checkBox24->UseVisualStyleBackColor = true;
			this->checkBox24->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox24_CheckedChanged);
			// 
			// textBox30
			// 
			this->textBox30->BackColor = System::Drawing::SystemColors::Info;
			this->textBox30->Enabled = false;
			this->textBox30->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->textBox30->Location = System::Drawing::Point(307, 34);
			this->textBox30->Name = L"textBox30";
			this->textBox30->Size = System::Drawing::Size(322, 26);
			this->textBox30->TabIndex = 1;
			// 
			// checkBox25
			// 
			this->checkBox25->AutoSize = true;
			this->checkBox25->Enabled = false;
			this->checkBox25->Location = System::Drawing::Point(436, 84);
			this->checkBox25->Name = L"checkBox25";
			this->checkBox25->Size = System::Drawing::Size(59, 20);
			this->checkBox25->TabIndex = 59;
			this->checkBox25->Text = L"Slot 3";
			this->checkBox25->UseVisualStyleBackColor = true;
			this->checkBox25->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox25_CheckedChanged);
			// 
			// checkBox26
			// 
			this->checkBox26->AutoSize = true;
			this->checkBox26->Enabled = false;
			this->checkBox26->Location = System::Drawing::Point(323, 82);
			this->checkBox26->Name = L"checkBox26";
			this->checkBox26->Size = System::Drawing::Size(59, 20);
			this->checkBox26->TabIndex = 58;
			this->checkBox26->Text = L"Slot 2";
			this->checkBox26->UseVisualStyleBackColor = true;
			this->checkBox26->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox26_CheckedChanged);
			// 
			// checkBox27
			// 
			this->checkBox27->AutoSize = true;
			this->checkBox27->Enabled = false;
			this->checkBox27->Location = System::Drawing::Point(210, 84);
			this->checkBox27->Name = L"checkBox27";
			this->checkBox27->Size = System::Drawing::Size(59, 20);
			this->checkBox27->TabIndex = 57;
			this->checkBox27->Text = L"Slot 1";
			this->checkBox27->UseVisualStyleBackColor = true;
			this->checkBox27->CheckedChanged += gcnew System::EventHandler(this, &Form1::checkBox27_CheckedChanged);
			// 
			// button9
			// 
			this->button9->Location = System::Drawing::Point(338, 644);
			this->button9->Name = L"button9";
			this->button9->Size = System::Drawing::Size(133, 60);
			this->button9->TabIndex = 51;
			this->button9->Text = L"Next Plate";
			this->button9->UseVisualStyleBackColor = true;
			this->button9->Click += gcnew System::EventHandler(this, &Form1::button9_Click);
			// 
			// button15
			// 
			this->button15->Location = System::Drawing::Point(502, 644);
			this->button15->Name = L"button15";
			this->button15->Size = System::Drawing::Size(117, 59);
			this->button15->TabIndex = 52;
			this->button15->Text = L"Next Plate Keep Dosimetry";
			this->button15->UseVisualStyleBackColor = true;
			this->button15->Click += gcnew System::EventHandler(this, &Form1::button15_Click);
			// 
			// Form1
			// 
			this->AutoScaleDimensions = System::Drawing::SizeF(8, 16);
			this->AutoScaleMode = System::Windows::Forms::AutoScaleMode::Font;
			this->ClientSize = System::Drawing::Size(1696, 742);
			this->Controls->Add(this->button15);
			this->Controls->Add(this->button9);
			this->Controls->Add(this->groupBox10);
			this->Controls->Add(this->groupBox9);
			this->Controls->Add(this->groupBox8);
			this->Controls->Add(this->groupBox7);
			this->Controls->Add(this->groupBox6);
			this->Controls->Add(this->groupBox5);
			this->Controls->Add(this->groupBox4);
			this->Controls->Add(this->groupBox3);
			this->Controls->Add(this->groupBox2);
			this->Controls->Add(this->groupBox1);
			this->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 9.75F, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->KeyPreview = true;
			this->Margin = System::Windows::Forms::Padding(3, 2, 3, 2);
			this->Name = L"Form1";
			this->Text = L"DAQ Application";
			this->KeyDown += gcnew System::Windows::Forms::KeyEventHandler(this, &Form1::Form1_KeyDown);
			this->KeyPress += gcnew System::Windows::Forms::KeyPressEventHandler(this, &Form1::Form1_KeyPress);
			this->KeyUp += gcnew System::Windows::Forms::KeyEventHandler(this, &Form1::Form1_KeyUp);
			this->groupBox1->ResumeLayout(false);
			this->groupBox1->PerformLayout();
			this->groupBox2->ResumeLayout(false);
			this->groupBox2->PerformLayout();
			this->groupBox3->ResumeLayout(false);
			this->groupBox3->PerformLayout();
			this->groupBox4->ResumeLayout(false);
			this->groupBox4->PerformLayout();
			(cli::safe_cast<System::ComponentModel::ISupportInitialize^>(this->chart1))->EndInit();
			this->groupBox5->ResumeLayout(false);
			this->groupBox5->PerformLayout();
			this->groupBox6->ResumeLayout(false);
			this->groupBox6->PerformLayout();
			this->groupBox7->ResumeLayout(false);
			this->groupBox7->PerformLayout();
			this->groupBox8->ResumeLayout(false);
			this->groupBox8->PerformLayout();
			this->groupBox9->ResumeLayout(false);
			this->groupBox9->PerformLayout();
			this->groupBox10->ResumeLayout(false);
			this->groupBox10->PerformLayout();
			this->ResumeLayout(false);

		}
#pragma endregion
	private: System::Void button1_Click(System::Object^ sender, System::EventArgs^ e) {
		//label1->Text = "Why Did You Do that?";
		//dataout = " ";
		PortDataReceived::Reader(dataout, textBox19->Text);
		std::string Bx, By, Bz, Th;
		label1->Text = msclr::interop::marshal_as<System::String^>(dataout[1]);
		int limEAN = dataout.size();
		array<System::String^>^ output = gcnew array<System::String^>(limEAN);
		int i1;
		//int i1 = dataout.size();
		for (i1 = 0; i1 < limEAN; i1++) {
			output[i1] = msclr::interop::marshal_as<System::String^>(dataout[i1]);
		}
		textBox1->Lines = output;
		textBox3->Text = output[limEAN-1];
		Tabparse(dataout[limEAN - 1], Bx, By, Bz, Th);
		/*textBox4->Text = msclr::interop::marshal_as<System::String^>(Bx);
		textBox5->Text = msclr::interop::marshal_as<System::String^>(By);
		textBox6->Text = msclr::interop::marshal_as<System::String^>(Bz);
		textBox7->Text = msclr::interop::marshal_as<System::String^>(Th);*/

	}
	private: System::Void button2_Click(System::Object^ sender, System::EventArgs^ e) {
		array<String^>^ serialports = nullptr;
		try
		{
			serialports = SerialPort::GetPortNames();
		}
		catch(Win32Exception^ ex){

		}
		textBox8->Lines = serialports;
	}
private: System::Void Form1_KeyDown(System::Object^ sender, System::Windows::Forms::KeyEventArgs^ e) {
	//if (Control::ModifierKeys == Keys::Alt && e->KeyCode != Keys::Alt) {
		//textBox2->ReadOnly = false;
		//textBox2->Select();
		//textBox2->AppendText(msclr::interop::marshal_as<System::String^>(std::to_string(e->ToString())));
		//textBox2->AppendText(e->KeyData.ToString());
		//e->SuppressKeyPress = false;
		//e->Handled = false;
		//wedge = true;
	//}
	std::string type, plate, slot;
	if (e->KeyCode == Keys::Oemtilde) {
		if (wedge || wedgeas || wedgeah) {
			Dashparse(msclr::interop::marshal_as<std::string>(textBox17->Text), type, plate, slot);
			textBox26->Text = msclr::interop::marshal_as<System::String^>(plate);
			textBox27->Text = msclr::interop::marshal_as<System::String^>(slot);
		}
		wedge = false; wedgesetup = false; wedgedos = false; wedgerod = false; wedgeas = false; wedgeah = false;
	}

}

private: System::Void Form1_KeyUp(System::Object^ sender, System::Windows::Forms::KeyEventArgs^ e) {
	//if (e->KeyCode == Keys::Alt) {
	//	textBox2->ReadOnly = true;
	//	wedge = false;
	//}
	//if (e->KeyCode == Keys::D4 && e->Modifiers==Keys::Shift) { wedge = true; }
	//if (e->KeyChar == '$') { wedge = true; }
}
private: System::Void Form1_KeyPress(System::Object^ sender, System::Windows::Forms::KeyPressEventArgs^ e) {
	//if (wedge) { label1->Text = "slam"; }
	//if (wedge) { textBox2->AppendText(msclr::interop::marshal_as<System::String^>(std::to_string(e->KeyChar))); }
	if (e->KeyChar == 'Y' && !readsam && checkBox7->Checked && !radioButton2->Checked) { wedge = true; radioButton1->Checked = true; readsam = true; }
	if (e->KeyChar == 'X' && !readdos && checkBox7->Checked) { wedgedos = true; readdos = true; }
	if (e->KeyChar == 'R' && !readrod && checkBox7->Checked) { wedgerod = true; readrod = true; }
	if ((e->KeyChar == 'A') && !wedge && !wedgedos && !wedgerod && checkBox7->Checked && !readsam && !radioButton1->Checked && !wedgesetup) { wedgeas = true; radioButton2->Checked = true; readsam = true; }
	if ((e->KeyChar == 'H') && !wedge && !wedgedos && !wedgerod && checkBox7->Checked && !readsam && !radioButton1->Checked && !wedgesetup) { wedgeah = true; radioButton3->Checked = true; readsam = true; }
	/*if (e->KeyChar == '\t') {
		wedgedos = false;
		e->Handled = true;
	}*/
	if (wedge || wedgeas || wedgeah) {
		//label1->Text = "slam";
		//e->Handled = false;
		textBox17->AppendText(e->KeyChar.ToString());
	}
	if (wedgesetup && !checkBox7->Checked) {
		//label1->Text = "slam";
		//e->Handled = false;
		textBox22->AppendText(e->KeyChar.ToString());
	}
	if (wedgedos) {
		//label1->Text = "slam";
		//e->Handled = false;
		textBox24->AppendText(e->KeyChar.ToString());
	}
	if (wedgerod) {
		//label1->Text = "slam";
		//e->Handled = false;
		textBox25->AppendText(e->KeyChar.ToString());
	}
	if (e->KeyChar == '$') { wedgesetup = true; }
}
private: System::Void textBox2_KeyPress(System::Object^ sender, System::Windows::Forms::KeyPressEventArgs^ e) {
	//label1->Text = e->KeyChar; 

}
private: System::Void button3_Click(System::Object^ sender, System::EventArgs^ e) {
	//label1->Text = "Why Did You Do that?";
//dataout = " ";
	int fr, ba, to;
	PortDataReceived::Ardmessagereceive(ardataout, textBox18->Text, "B");
	//label1->Text = msclr::interop::marshal_as<System::String^>(ardataout[1]);
	int limEAN = ardataout.size();
	array<System::String^>^ output2 = gcnew array<System::String^>(limEAN);
	int i1;
	//int i1 = dataout.size();
	for (i1 = 0; i1 < limEAN; i1++) {
		output2[i1] = msclr::interop::marshal_as<System::String^>(ardataout[i1]);
	}
	textBox2->Lines = output2;
	ardparse(ardataout[limEAN - 1], fr, ba, to);
	if (fr < fco) { checkBox1->Checked = true; } else { checkBox1->Checked = false; }
	if (ba < sco) { checkBox2->Checked = true; } else { checkBox2->Checked = false; }
	if (to < tco) { checkBox3->Checked = true; } else { checkBox3->Checked = false; }
}
private: System::Void textBox11_TextChanged(System::Object^ sender, System::EventArgs^ e) {
}
private: System::Void button4_Click(System::Object^ sender, System::EventArgs^ e) {
	int fr, ba, to;
	System::Windows::Forms::DialogResult msgboxID;
	bool worked = true;
	bool worked2 = true;

	if (radioButton1->Checked && checkBox4->Checked) {
		try {
			PortDataReceived::Ardmessagereceive(ardataout, textBox18->Text, "B");
		}
		catch (System::IO::IOException^ ent) {
			worked = false;
			msgboxID = MessageBox::Show(
				this,
				"Arduino not Connected\ncheck connection and try again",
				"Device Not Connected",
				MessageBoxButtons::OK
			);

		}
		if (worked) {
			//label1->Text = msclr::interop::marshal_as<System::String^>(ardataout[1]);
			int limEANA = ardataout.size();
			array<System::String^>^ output2 = gcnew array<System::String^>(limEANA);
			int i1;
			//int i1 = dataout.size();
			for (i1 = 0; i1 < limEANA; i1++) {
				output2[i1] = msclr::interop::marshal_as<System::String^>(ardataout[i1]);
			}
			textBox2->Lines = output2;
			ardparse(ardataout[limEANA - 1], fr, ba, to);

			if (fr < fco) { checkBox1->Checked = true; }
			else { checkBox1->Checked = false; }
			if (ba < sco) { checkBox2->Checked = true; }
			else { checkBox2->Checked = false; }
			if (to < tco*1.2) { checkBox3->Checked = true; }
			else { checkBox3->Checked = false; }
		}
	} else if(radioButton2->Checked && checkBox4->Checked) {
		try {
			PortDataReceived::Ardmessagereceive(ardataout, textBox18->Text, "Q");
		}
		catch (System::IO::IOException^ ent) {
			worked = false;
			msgboxID = MessageBox::Show(
				this,
				"Arduino not Connected\ncheck connection and try again",
				"Device Not Connected",
				MessageBoxButtons::OK
			);

		}
		if (worked) {
			//label1->Text = msclr::interop::marshal_as<System::String^>(ardataout[1]);
			int limEANA = ardataout.size();
			array<System::String^>^ output2 = gcnew array<System::String^>(limEANA);
			int i1;
			//int i1 = dataout.size();
			for (i1 = 0; i1 < limEANA; i1++) {
				output2[i1] = msclr::interop::marshal_as<System::String^>(ardataout[i1]);
			}
			textBox2->Lines = output2;
			ardparse(ardataout[limEANA - 1], to, ba, fr);

			if (fr < afco) { checkBox1->Checked = true; }
			else { checkBox1->Checked = false; }
			if (ba < asco) { checkBox2->Checked = true; }
			else { checkBox2->Checked = false; }
			if (to < atco) { checkBox3->Checked = true; }
			else { checkBox3->Checked = false; }
		}
	}
	else if (radioButton3->Checked && checkBox4->Checked) {
		try {
		PortDataReceived::Ardmessagereceive(ardataout, textBox18->Text, "Q");
		}
		catch (System::IO::IOException^ ent) {
			worked = false;
			msgboxID = MessageBox::Show(
				this,
				"Arduino not Connected\ncheck connection and try again",
				"Device Not Connected",
				MessageBoxButtons::OK
			);

		}
		if (worked) {
			//label1->Text = msclr::interop::marshal_as<System::String^>(ardataout[1]);
			int limEANA = ardataout.size();
			array<System::String^>^ output2 = gcnew array<System::String^>(limEANA);
			int i1;
			//int i1 = dataout.size();
			for (i1 = 0; i1 < limEANA; i1++) {
				output2[i1] = msclr::interop::marshal_as<System::String^>(ardataout[i1]);
			}
			textBox2->Lines = output2;
			ardparse(ardataout[limEANA - 1], to, ba, fr);
			//if (to < ahtco) { checkBox37->Checked = true; }
			//else { checkBox37->Checked = false; }
			if (fr < ahfco) { checkBox1->Checked = true; }
			else { checkBox1->Checked = false; }
			if (ba < ahsco) { checkBox2->Checked = true; }
			else { checkBox2->Checked = false; }
			if (to < ahtco) { checkBox3->Checked = true; }
			else { checkBox3->Checked = false; }
		}
	}
	if ((checkBox1->Checked && checkBox2->Checked) || (checkBox1->Checked && checkBox3->Checked) || (checkBox2->Checked && checkBox3->Checked)) {
		msgboxID = MessageBox::Show(
			this,
			"Multiple slots activated\nCheck wiring",
			"Input Error",
			MessageBoxButtons::OK
		);
		worked2 = false;
	}
	if (checkBox5->Checked) {
		try{
		PortDataReceived::Reader(dataout, textBox19->Text);
		}
		catch (System::IO::IOException^ ent) {
			worked2 = false;
			msgboxID = MessageBox::Show(
				this,
				"Teslameter not Connected\ncheck connection and try again",
				"Device Not Connected",
				MessageBoxButtons::OK
			);

		}
		if (worked2) {
			std::string Bx, By, Bz, Th;
			//label1->Text = msclr::interop::marshal_as<System::String^>(dataout[1]);
			int limEAN = dataout.size();

			array<System::String^>^ output = gcnew array<System::String^>(limEAN);
			int i1;
			//int i1 = dataout.size();
			for (i1 = 0; i1 < limEAN; i1++) {
				output[i1] = msclr::interop::marshal_as<System::String^>(dataout[i1]);
			}
			textBox1->Lines = output;
			textBox3->Text = output[limEAN - 1];
			Tabparse(dataout[limEAN - 1], Bx, By, Bz, Th);
			if (checkBox1->Checked == true) {
				textBox4->Text = msclr::interop::marshal_as<System::String^>(Bx);
				textBox5->Text = msclr::interop::marshal_as<System::String^>(By);
				textBox6->Text = msclr::interop::marshal_as<System::String^>(Bz);
				textBox7->Text = msclr::interop::marshal_as<System::String^>(Th);
			}
			if (checkBox2->Checked == true) {
				textBox9->Text = msclr::interop::marshal_as<System::String^>(Bx);
				textBox10->Text = msclr::interop::marshal_as<System::String^>(By);
				textBox11->Text = msclr::interop::marshal_as<System::String^>(Bz);
				textBox12->Text = msclr::interop::marshal_as<System::String^>(Th);
			}
			if (checkBox3->Checked == true) {
				textBox13->Text = msclr::interop::marshal_as<System::String^>(Bx);
				textBox14->Text = msclr::interop::marshal_as<System::String^>(By);
				textBox15->Text = msclr::interop::marshal_as<System::String^>(Bz);
				textBox16->Text = msclr::interop::marshal_as<System::String^>(Th);
			}
		}
	}
}
private: System::Void button5_Click(System::Object^ sender, System::EventArgs^ e) {
	std::ofstream output1;
	time_t rawtime;
	char buffer[80];
	struct tm* timeinfo;
	System::Windows::Forms::DialogResult msgboxID;

	if (textBox17->TextLength > 0) {
		//time_t timeinfo;
		time(&rawtime);
		timeinfo = localtime(&rawtime);
		strftime(buffer, 80, " %F\t%T", timeinfo);
		if (checkBox16->Checked) {
			output1.open(msclr::interop::marshal_as<std::string>(textBox23->Text + textBox17->Text + "_front.dat"), std::ios::app);
			output1 << buffer << '\t' << msclr::interop::marshal_as<std::string>(textBox24->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox25->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox4->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox5->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox6->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox7->Text) << '\n';
			output1.close();
		}
		if (checkBox17->Checked) {
			output1.open(msclr::interop::marshal_as<std::string>(textBox23->Text + textBox17->Text + "_side.dat"), std::ios::app);
			output1 << buffer << '\t' << msclr::interop::marshal_as<std::string>(textBox24->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox25->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox9->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox10->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox11->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox12->Text) << '\n';
			output1.close();
		}
		if (checkBox18->Checked) {
			output1.open(msclr::interop::marshal_as<std::string>(textBox23->Text + textBox17->Text + "_top.dat"), std::ios::app);
			output1 << buffer << '\t' << msclr::interop::marshal_as<std::string>(textBox24->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox25->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox13->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox14->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox15->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox16->Text) << '\n';
			output1.close();
		}
		if (textBox27->Text == "4" || textBox27->Text == "4-1") { checkBox11->Checked = true; }
		if (textBox27->Text == "3" || textBox27->Text == "3-1") { checkBox10->Checked = true; }
		if (textBox27->Text == "2" || textBox27->Text == "2-1") { checkBox9->Checked = true; }
		if (textBox27->Text == "1" || textBox27->Text == "1-1") { checkBox8->Checked = true; }
		if (textBox27->Text == "4-2") { checkBox12->Checked = true; }
		if (textBox27->Text == "3-2") { checkBox13->Checked = true; }
		if (textBox27->Text == "2-2") { checkBox14->Checked = true; }
		if (textBox27->Text == "1-2") { checkBox15->Checked = true; }
		//readsam = false;
		textBox4->Text = "";
		textBox5->Text = "";
		textBox6->Text = "";
		textBox7->Text = "";
		textBox8->Text = "";
		textBox9->Text = "";
		textBox10->Text = "";
		textBox11->Text = "";
		textBox12->Text = "";
		textBox13->Text = "";
		textBox14->Text = "";
		textBox15->Text = "";
		textBox16->Text = "";
		//textBox17->Text = "";
		//textBox26->Text = "";
		//textBox27->Text = "";
		checkBox1->Checked = false;
		checkBox2->Checked = false;
		checkBox3->Checked = false;
		checkBox16->Checked = false;
		checkBox17->Checked = false;
		checkBox18->Checked = false;
	} else {
		msgboxID = MessageBox::Show(
			this,
			"No Sample Number\nScan magnet barcode before proceeding",
			"No Sample Scanned",
			MessageBoxButtons::OK
		);
	}
}
private: System::Void button6_Click(System::Object^ sender, System::EventArgs^ e) {
	int fr, si, to;
	int afr, asi, ato;
	int ahto, ahsi, ahfr;
	int afrb, asib, atob;
	int frb, sib, tob,gar,gar1;
	bool worked = true;
	System::Windows::Forms::DialogResult msgboxID;
	progressBar1->Value = 0;
	ardataout.push_back("Single Sample");
	try {
	PortDataReceived::Ardmessagereceive(ardataout, textBox18->Text, "B");
}
	   catch (System::IO::IOException^ ent) {
		   worked = false;
		   msgboxID = MessageBox::Show(
			   this,
			   "Arduino not Connected\ncheck connection and try again",
			   "Device Not Connected",
			   MessageBoxButtons::OK
		   );

	   }
	   if (worked) {
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessage(textBox18->Text, "lp7off");
		   PortDataReceived::Ardmessage(textBox18->Text, "lp8off");
		   PortDataReceived::Ardmessage(textBox18->Text, "lp9off");
		   PortDataReceived::Ardmessage(textBox18->Text, "lp1on");
		   PortDataReceived::Ardmessage(textBox18->Text, "lp2on");
		   PortDataReceived::Ardmessage(textBox18->Text, "lp3on");
		   progressBar1->PerformStep();
		   //PortDataReceived::ArdLights("COM4");
		   //Sleep(250);
		   PortDataReceived::Ardmessagereceive(ardataout, textBox18->Text, "B");
		   progressBar1->PerformStep();
		   ardparse(ardataout[ardataout.size() - 1], fr, si, to);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessage(textBox18->Text, "lp1off");
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessagereceive(ardataout, textBox18->Text, "B");
		   progressBar1->PerformStep();
		   ardparse(ardataout[ardataout.size() - 1], gar, gar1, tob);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessage(textBox18->Text, "lp1on");
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessage(textBox18->Text, "lp2off");
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessagereceive(ardataout, textBox18->Text, "B");
		   progressBar1->PerformStep();
		   ardparse(ardataout[ardataout.size() - 1], frb, gar1, gar);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessage(textBox18->Text, "lp2on");
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessage(textBox18->Text, "lp3off");
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessagereceive(ardataout, textBox18->Text, "B");
		   progressBar1->PerformStep();
		   ardparse(ardataout[ardataout.size() - 1], gar1, sib, gar);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessage(textBox18->Text, "lp3on");
		   progressBar1->PerformStep();
		   fco = (fr + frb) / 2;
		   sco = (si + sib) / 2;
		   tco = (to + tob) / 2;
		   progressBar1->PerformStep();
		   ardataout.push_back("Assembly Sample");
		   progressBar1->Value = 0;
		   PortDataReceived::Ardmessagereceive(ardataout, textBox18->Text, "Q");
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessage(textBox18->Text, "lp4on");
		   PortDataReceived::Ardmessage(textBox18->Text, "lp5on");
		   PortDataReceived::Ardmessage(textBox18->Text, "lp6on");
		   progressBar1->PerformStep();
		   Sleep(10);
		   //PortDataReceived::ArdLights("COM4");
		   //Sleep(250);
		   PortDataReceived::Ardmessagereceive(ardataout, textBox18->Text, "Q");
		   progressBar1->PerformStep();
		   ardparse(ardataout[ardataout.size() - 1], ato, asi, afr);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessage(textBox18->Text, "lp4off");
		   Sleep(10);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessagereceive(ardataout, textBox18->Text, "Q");
		   progressBar1->PerformStep();
		   ardparse(ardataout[ardataout.size() - 1], atob, gar, gar1);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessage(textBox18->Text, "lp4on");
		   progressBar1->PerformStep();
		   Sleep(10);
		   PortDataReceived::Ardmessage(textBox18->Text, "lp5off");
		   Sleep(10);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessagereceive(ardataout, textBox18->Text, "Q");
		   progressBar1->PerformStep();
		   ardparse(ardataout[ardataout.size() - 1], gar1, asib, gar);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessage(textBox18->Text, "lp5on");
		   Sleep(10);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessage(textBox18->Text, "lp6off");
		   Sleep(10);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessagereceive(ardataout, textBox18->Text, "Q");
		   progressBar1->PerformStep();
		   ardparse(ardataout[ardataout.size() - 1], gar1, gar, afrb);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessage(textBox18->Text, "lp6on");
		   progressBar1->PerformStep();
		   afco = (afr + afrb) / 2;
		   asco = (asi + asib) / 2;
		   atco = (ato + atob) / 2;
		   progressBar1->PerformStep();

		   PortDataReceived::Ardmessage(textBox18->Text, "lp4off");
		   PortDataReceived::Ardmessage(textBox18->Text, "lp5off");
		   PortDataReceived::Ardmessage(textBox18->Text, "lp6off");
		   Sleep(10);
		   ardataout.push_back("Assembly Holder");
		   PortDataReceived::Ardmessage(textBox18->Text, "lp7on");
		   PortDataReceived::Ardmessage(textBox18->Text, "lp8on");
		   PortDataReceived::Ardmessage(textBox18->Text, "lp9on");
		   Sleep(10);
		   PortDataReceived::Ardmessagereceive(ardataout, textBox18->Text, "Q");
		   progressBar1->PerformStep();
		   ardparse(ardataout[ardataout.size() - 1], ahto, ahsi, ahfr);

		   PortDataReceived::Ardmessage(textBox18->Text, "lp7off");
		   Sleep(10);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessagereceive(ardataout, textBox18->Text, "Q");
		   progressBar1->PerformStep();
		   ardparse(ardataout[ardataout.size() - 1], atob, gar, gar1);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessage(textBox18->Text, "lp7on");
		   progressBar1->PerformStep();
		   Sleep(10);
		   PortDataReceived::Ardmessage(textBox18->Text, "lp8off");
		   Sleep(10);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessagereceive(ardataout, textBox18->Text, "Q");
		   progressBar1->PerformStep();
		   ardparse(ardataout[ardataout.size() - 1], gar1, asib, gar);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessage(textBox18->Text, "lp8on");
		   Sleep(10);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessage(textBox18->Text, "lp9off");
		   Sleep(10);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessagereceive(ardataout, textBox18->Text, "Q");
		   progressBar1->PerformStep();
		   ardparse(ardataout[ardataout.size() - 1], gar1, gar, afrb);
		   progressBar1->PerformStep();
		   PortDataReceived::Ardmessage(textBox18->Text, "lp9on");

		   //PortDataReceived::Ardmessage(textBox18->Text, "lp7off");
		   //PortDataReceived::Ardmessage(textBox18->Text, "lp4on");
		   ahtco = (ahto + atob) / 2;
		   ahsco = (ahsi + asib) / 2;
		   ahfco = (ahfr + afrb) / 2;

		   int limEAN = ardataout.size();
		   array<System::String^>^ output2 = gcnew array<System::String^>(limEAN);
		   int i1;
		   //int i1 = dataout.size();
		   for (i1 = 0; i1 < limEAN; i1++) {
			   output2[i1] = msclr::interop::marshal_as<System::String^>(ardataout[i1]);
		   }
		   progressBar1->PerformStep();
		   textBox2->Lines = output2;
		   checkBox4->Checked = true;
		   if (radioButton2->Checked) {
			   PortDataReceived::Ardmessage(textBox18->Text, "lp7off");
			   PortDataReceived::Ardmessage(textBox18->Text, "lp8off");
			   PortDataReceived::Ardmessage(textBox18->Text, "lp9off");
			   PortDataReceived::Ardmessage(textBox18->Text, "lp4on");
			   PortDataReceived::Ardmessage(textBox18->Text, "lp5on");
			   PortDataReceived::Ardmessage(textBox18->Text, "lp6on");
		   }
	   }
}
private: System::Void button7_Click(System::Object^ sender, System::EventArgs^ e) {
	std::string dummystring;
	bool worked = true;
	System::Windows::Forms::DialogResult msgboxID;
	//PortDataReceived::Reader(dataout,textBox19->Text);
	try {
		//PortDataReceived::Ardmessagereceive(dataout, textBox19->Text, "t");
		PortDataReceived::Reader(dataout, textBox19->Text);
	} catch (System::IO::IOException^ ent) {
		worked = false;
		msgboxID = MessageBox::Show(
			this,
			"Teslameter not Connected\ncheck connection and try again",
			"Device Not Connected",
			MessageBoxButtons::OK 
		);

	} catch (TimeoutException^ ex) {
		worked = false;
		msgboxID = System::Windows::Forms::MessageBox::Show(
			this,
			"It's doing that weird thing\n unplug the teslameter and plug it back in again",
			"Device Not Responding",
			MessageBoxButtons::OK
		);
	}
	catch (UnauthorizedAccessException^ ex) {
		worked = false;
		msgboxID = System::Windows::Forms::MessageBox::Show(
			this,
			"It's doing that weird thing\n unplug the teslameter and plug it back in again",
			"Device Not Responding",
			MessageBoxButtons::OK
		);
	}
	if (worked) {
		int limEAN = dataout.size();
		dummystring = "Teslameter information :\n";

		if (dataout[limEAN - 18].substr(0, 10) == "Teslameter") {
			textBox20->Text = msclr::interop::marshal_as<System::String^>(dataout[limEAN - 17]);
			checkBox5->Checked = true;
		}
	}
}
private: System::Void checkBox6_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	groupBox4->Visible = checkBox6->Checked;
}
private: System::Void textBox22_TextChanged(System::Object^ sender, System::EventArgs^ e) {
	if (textBox22->Text == textBox21->Text) { checkBox7->Checked = true; }
}
private: System::Void button8_Click(System::Object^ sender, System::EventArgs^ e) {
	if (folderBrowserDialog1->ShowDialog() == System::Windows::Forms::DialogResult::OK) { textBox23->Text = folderBrowserDialog1->SelectedPath+"\\"; }
}
private: System::Void radioButton2_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	checkBox12->Visible = radioButton2->Checked;
	checkBox13->Visible = radioButton2->Checked;
	checkBox14->Visible = radioButton2->Checked;
	checkBox15->Visible = radioButton2->Checked;
	checkBox23->Visible = radioButton2->Checked;
	checkBox22->Visible = radioButton2->Checked;
	checkBox21->Visible = radioButton2->Checked;
	checkBox20->Visible = radioButton2->Checked;
	checkBox31->Visible = radioButton2->Checked;
	checkBox30->Visible = radioButton2->Checked;
	checkBox29->Visible = radioButton2->Checked;
	checkBox28->Visible = radioButton2->Checked;
	if (radioButton2->Checked) {
		checkBox8->Text = "Slot 1-1";
		checkBox9->Text = "Slot 2-1";
		checkBox10->Text = "Slot 3-1";
		checkBox11->Text = "Slot 4-1";
		checkBox27->Text = "Slot 1-1";
		checkBox26->Text = "Slot 2-1";
		checkBox25->Text = "Slot 3-1";
		checkBox24->Text = "Slot 4-1";
		checkBox35->Text = "Slot 1-1";
		checkBox34->Text = "Slot 2-1";
		checkBox33->Text = "Slot 3-1";
		checkBox32->Text = "Slot 4-1";
		if (!radioButton3->Checked) {
			PortDataReceived::Ardmessage(textBox18->Text, "lp7off");
			PortDataReceived::Ardmessage(textBox18->Text, "lp8off");
			PortDataReceived::Ardmessage(textBox18->Text, "lp9off");
			PortDataReceived::Ardmessage(textBox18->Text, "lp4on");
			PortDataReceived::Ardmessage(textBox18->Text, "lp5on");
			PortDataReceived::Ardmessage(textBox18->Text, "lp6on");
		}
	}
	else {
		checkBox8->Text = "Slot 1";
		checkBox9->Text = "Slot 2";
		checkBox10->Text = "Slot 3";
		checkBox11->Text = "Slot 4";
		checkBox27->Text = "Slot 1";
		checkBox26->Text = "Slot 2";
		checkBox25->Text = "Slot 3";
		checkBox24->Text = "Slot 4";
		checkBox35->Text = "Slot 1";
		checkBox34->Text = "Slot 2";
		checkBox33->Text = "Slot 3";
		checkBox32->Text = "Slot 4";
	}
}
private: System::Void button9_Click(System::Object^ sender, System::EventArgs^ e) {
	radioButton1->Checked = false;
	radioButton2->Checked = false;
	radioButton3->Checked = false;
	textBox24->Text = "";
	textBox25->Text = "";
	textBox26->Text = "";
	textBox27->Text = "";
	textBox17->Text = "";
	textBox4->Text = "";
	textBox5->Text = "";
	textBox6->Text = "";
	textBox7->Text = "";
	textBox8->Text = "";
	textBox9->Text = "";
	textBox10->Text = "";
	textBox11->Text = "";
	textBox12->Text = "";
	textBox13->Text = "";
	textBox14->Text = "";
	textBox15->Text = "";
	textBox16->Text = "";
	textBox30->Text = "";
	readdos = false;
	readrod = false;
	readsam = false;
	checkBox8->Checked = false;
	checkBox9->Checked = false;
	checkBox10->Checked = false;
	checkBox11->Checked = false;
	checkBox12->Checked = false;
	checkBox13->Checked = false;
	checkBox14->Checked = false;
	checkBox15->Checked = false;
	checkBox28->Checked = false;
	checkBox29->Checked = false;
	checkBox30->Checked = false;
	checkBox31->Checked = false;
	checkBox32->Checked = false;
	checkBox33->Checked = false;
	checkBox34->Checked = false;
	checkBox35->Checked = false;
	checkBox27->Checked = false;
	checkBox26->Checked = false;
	checkBox25->Checked = false;
	checkBox24->Checked = false;
	checkBox23->Checked = false;
	checkBox22->Checked = false;
	checkBox21->Checked = false;
	checkBox20->Checked = false;
}
private: System::Void textBox24_TextChanged(System::Object^ sender, System::EventArgs^ e) {
//	if (textBox24->Text->Length == 11) { wedgedos = false; }
}
private: System::Void checkBox1_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox1->Checked) { checkBox16->Checked = true; }
}
private: System::Void checkBox2_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox2->Checked) { checkBox17->Checked = true; }
}
private: System::Void checkBox3_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox3->Checked) { checkBox18->Checked = true; }
}
private: System::Void button10_Click(System::Object^ sender, System::EventArgs^ e) {
	std::vector<std::string> helmdata;
	System::Windows::Forms::DialogResult msgboxID;
	bool worked = true;
	try{
	PortDataReceived::Ardmessagereceive(helmdata,textBox28->Text, "B");
}
	   catch (System::IO::IOException^ ent) {
		   worked = false;
		   msgboxID = MessageBox::Show(
			   this,
			   "Helmholtz Coil not Connected\ncheck connection and try again",
			   "Device Not Connected",
			   MessageBoxButtons::OK
		   );

	   }
	   if (worked) {
		   textBox29->Text = msclr::interop::marshal_as<System::String^>(helmdata[0]);
	   }
}
private: System::Void button11_Click(System::Object^ sender, System::EventArgs^ e) {
	std::vector<std::string> helmdata;
	System::Windows::Forms::DialogResult msgboxID;
	bool worked = true;
	try{
	PortDataReceived::Ardmessagereceive(helmdata, textBox28->Text, "I");
	}
	catch (System::IO::IOException^ ent) {
		worked = false;
		msgboxID = MessageBox::Show(
			this,
			"Helmholtz Coil not Connected\ncheck connection and try again",
			"Device Not Connected",
			MessageBoxButtons::OK
		);

	}
	if (worked) {
		textBox30->Text = msclr::interop::marshal_as<System::String^>(helmdata[0].substr(1, helmdata[0].size()));
		checkBox19->Checked = true;
	}
}
private: System::Void button12_Click(System::Object^ sender, System::EventArgs^ e) {
	std::ofstream output1;
	System::Windows::Forms::DialogResult msgboxID;
	time_t rawtime;
	char buffer[80];
	struct tm* timeinfo;
	//time_t timeinfo;

	if (textBox17->TextLength > 0) {
	time(&rawtime);
	timeinfo = localtime(&rawtime);
	strftime(buffer, 80, " %F\t%T", timeinfo);

	output1.open(msclr::interop::marshal_as<std::string>(textBox23->Text + textBox17->Text + "_helmholtz.dat"), std::ios::app);
	output1 << buffer << '\t' << msclr::interop::marshal_as<std::string>(textBox24->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox25->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox30->Text) << '\n';
	output1.close();
	
	if (textBox27->Text == "4" || textBox27->Text == "4-1") { checkBox24->Checked = true; }
	if (textBox27->Text == "3" || textBox27->Text == "3-1") { checkBox25->Checked = true; }
	if (textBox27->Text == "2" || textBox27->Text == "2-1") { checkBox26->Checked = true; }
	if (textBox27->Text == "1" || textBox27->Text == "1-1") { checkBox27->Checked = true; }
	if (textBox27->Text == "4-2") { checkBox20->Checked = true; }
	if (textBox27->Text == "3-2") { checkBox21->Checked = true; }
	if (textBox27->Text == "2-2") { checkBox22->Checked = true; }
	if (textBox27->Text == "1-2") { checkBox23->Checked = true; }
	/*readsam = false;
	textBox4->Text = "";
	textBox5->Text = "";
	textBox6->Text = "";
	textBox7->Text = "";
	textBox8->Text = "";
	textBox9->Text = "";
	textBox10->Text = "";
	textBox11->Text = "";
	textBox12->Text = "";
	textBox13->Text = "";
	textBox14->Text = "";
	textBox15->Text = "";
	textBox16->Text = "";
	textBox17->Text = "";
	//textBox26->Text = "";
	textBox27->Text = "";
	checkBox1->Checked = false;
	checkBox2->Checked = false;
	checkBox3->Checked = false;
	checkBox16->Checked = false;
	checkBox17->Checked = false;
	checkBox18->Checked = false;*/
	checkBox19->Checked = false;
	textBox30->Text = "";
}
 else {
	msgboxID = MessageBox::Show(
		this,
		"No Sample Number\nScan magnet barcode before proceeding",
		"No Sample Scanned",
		MessageBoxButtons::OK
	);
	}
}
private: System::Void checkBox27_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox27->Checked && (checkBox8->Checked || !checkBox5->Checked)) { checkBox35->Checked = true; }
}
private: System::Void checkBox8_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox8->Checked && (checkBox27->Checked || !checkBox36->Checked)) { checkBox35->Checked = true; }
}
private: System::Void checkBox35_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox35->Checked) { readsam = false; textBox27->Text = ""; textBox17->Text = ""; }
}
private: System::Void checkBox9_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox9->Checked && (checkBox26->Checked || !checkBox36->Checked)) { checkBox34->Checked = true; }
}
private: System::Void checkBox10_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox10->Checked && (checkBox25->Checked || !checkBox36->Checked)) { checkBox33->Checked = true; }
}
private: System::Void checkBox11_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox11->Checked && (checkBox24->Checked || !checkBox36->Checked)) { checkBox32->Checked = true; }
}
private: System::Void checkBox12_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox12->Checked && (checkBox20->Checked || !checkBox36->Checked)) { checkBox28->Checked = true; }
}
private: System::Void checkBox13_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox13->Checked && (checkBox21->Checked || !checkBox36->Checked)) { checkBox29->Checked = true; }
}
private: System::Void checkBox14_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox14->Checked && (checkBox22->Checked || !checkBox36->Checked)) { checkBox30->Checked = true; }
}
private: System::Void checkBox15_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox15->Checked && (checkBox23->Checked || !checkBox36->Checked)) { checkBox31->Checked = true; }
}
private: System::Void checkBox26_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox26->Checked && (checkBox9->Checked || !checkBox5->Checked)) { checkBox34->Checked = true; }
}
private: System::Void checkBox25_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox25->Checked && (checkBox10->Checked || !checkBox5->Checked)) { checkBox33->Checked = true; }
}
private: System::Void checkBox24_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox24->Checked && (checkBox11->Checked || !checkBox5->Checked)) { checkBox32->Checked = true; }
}
private: System::Void checkBox20_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox20->Checked && (checkBox12->Checked || !checkBox5->Checked)) { checkBox28->Checked = true; }
}
private: System::Void checkBox21_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox21->Checked && (checkBox13->Checked || !checkBox5->Checked)) { checkBox29->Checked = true; }
}
private: System::Void checkBox22_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox22->Checked && (checkBox14->Checked || !checkBox5->Checked)) { checkBox30->Checked = true; }
}
private: System::Void checkBox23_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox23->Checked && (checkBox15->Checked || !checkBox5->Checked)) { checkBox31->Checked = true; }
}
private: System::Void checkBox34_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox34->Checked) { readsam = false; textBox27->Text = ""; textBox17->Text = ""; }
}
private: System::Void checkBox33_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox33->Checked) { readsam = false; textBox27->Text = ""; textBox17->Text = ""; }
}
private: System::Void checkBox32_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox32->Checked) { readsam = false; textBox27->Text = ""; textBox17->Text = ""; }
}
private: System::Void checkBox28_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox28->Checked) { readsam = false; textBox27->Text = ""; textBox17->Text = ""; }
}
private: System::Void checkBox29_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox29->Checked) { readsam = false; textBox27->Text = ""; textBox17->Text = ""; }
}
private: System::Void checkBox30_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox30->Checked) { readsam = false; textBox27->Text = ""; textBox17->Text = ""; }
}
private: System::Void checkBox31_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox31->Checked) { readsam = false; textBox27->Text = ""; textBox17->Text = ""; }
}
private: System::Void radioButton3_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox4->Checked) {
		if (radioButton3->Checked) {
			PortDataReceived::Ardmessage(textBox18->Text, "lp4off");
			PortDataReceived::Ardmessage(textBox18->Text, "lp5off");
			PortDataReceived::Ardmessage(textBox18->Text, "lp6off");
			PortDataReceived::Ardmessage(textBox18->Text, "lp7on");
			PortDataReceived::Ardmessage(textBox18->Text, "lp8on");
			PortDataReceived::Ardmessage(textBox18->Text, "lp9on");
		}
		else {
			PortDataReceived::Ardmessage(textBox18->Text, "lp7off");
			PortDataReceived::Ardmessage(textBox18->Text, "lp8off");
			PortDataReceived::Ardmessage(textBox18->Text, "lp9off");
			PortDataReceived::Ardmessage(textBox18->Text, "lp4on");
			PortDataReceived::Ardmessage(textBox18->Text, "lp5on");
			PortDataReceived::Ardmessage(textBox18->Text, "lp6on");
		}
	}
}
private: System::Void checkBox38_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox38->Checked) {
		textBox24->Enabled = true;
		textBox25->Enabled = true;
		textBox17->Enabled = true;
		textBox26->Enabled = true;
		textBox27->Enabled = true;
		checkBox7->Enabled = true;
		checkBox37->Enabled = true;
		radioButton1->Enabled = true;
		radioButton2->Enabled = true;
		radioButton3->Enabled = true;
	}
	else {
		textBox24->Enabled = false;
		textBox25->Enabled = false;
		textBox17->Enabled = false;
		textBox26->Enabled = false;
		textBox27->Enabled = false;
		checkBox7->Enabled = false;
		checkBox37->Enabled = false;
		radioButton1->Enabled = false;
		radioButton2->Enabled = false;
		radioButton3->Enabled = false;
	}
}
private: System::Void checkBox37_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	if (checkBox37->Checked) {
		label21->Text = "Seriously consider postponing data collection \n if you are at this point";
	}
	else { label21->Text = " "; }
	checkBox1->Enabled = checkBox37->Checked;
	checkBox2->Enabled = checkBox37->Checked;
	checkBox3->Enabled = checkBox37->Checked;
	checkBox13->Enabled = checkBox37->Checked;
	checkBox14->Enabled = checkBox37->Checked;
	checkBox15->Enabled = checkBox37->Checked;
	checkBox16->Enabled = checkBox37->Checked;
	checkBox17->Enabled = checkBox37->Checked;
	checkBox18->Enabled = checkBox37->Checked;
	checkBox28->Enabled = checkBox37->Checked;
	checkBox19->Enabled = checkBox37->Checked;
	checkBox29->Enabled = checkBox37->Checked;
	checkBox30->Enabled = checkBox37->Checked;
	checkBox31->Enabled = checkBox37->Checked;
	checkBox32->Enabled = checkBox37->Checked;
	checkBox33->Enabled = checkBox37->Checked;
	checkBox34->Enabled = checkBox37->Checked;
	checkBox35->Enabled = checkBox37->Checked;
	checkBox8->Enabled = checkBox37->Checked;
	checkBox9->Enabled = checkBox37->Checked;
	checkBox10->Enabled = checkBox37->Checked;
	checkBox11->Enabled = checkBox37->Checked;
	checkBox12->Enabled = checkBox37->Checked;
	checkBox20->Enabled = checkBox37->Checked;
	checkBox21->Enabled = checkBox37->Checked;
	checkBox22->Enabled = checkBox37->Checked;
	checkBox23->Enabled = checkBox37->Checked;
	checkBox24->Enabled = checkBox37->Checked;
	checkBox25->Enabled = checkBox37->Checked;
	checkBox26->Enabled = checkBox37->Checked;
	checkBox27->Enabled = checkBox37->Checked;
	textBox4->ReadOnly = !checkBox37->Checked;
	textBox5->ReadOnly = !checkBox37->Checked;
	textBox6->ReadOnly = !checkBox37->Checked;
	textBox7->ReadOnly = !checkBox37->Checked;
	textBox9->ReadOnly = !checkBox37->Checked;
	textBox10->ReadOnly = !checkBox37->Checked;
	textBox11->ReadOnly = !checkBox37->Checked;
	textBox12->ReadOnly = !checkBox37->Checked;
	textBox13->ReadOnly = !checkBox37->Checked;
	textBox14->ReadOnly = !checkBox37->Checked;
	textBox15->ReadOnly = !checkBox37->Checked;
	textBox16->ReadOnly = !checkBox37->Checked;
	textBox30->ReadOnly = !checkBox37->Checked;
}
private: System::Void button13_Click(System::Object^ sender, System::EventArgs^ e) {
	std::vector<std::string> helmdata;
	//std::vector<System::String^> helmdata2;
	System::Windows::Forms::DialogResult msgboxID;
	//System::Series^ series1 = (gcnew Series());
	//chart1->Series->Add(series1);
	float max = -100.0;
	int i,j,maxint;
	bool worked = true;
	progressBar2->Value = 0;
	chart1->Series[0]->Points->Clear();
	for (i = 0; i < 30; i++) {
		try {
			PortDataReceived::Ardmessagereceive(helmdata, textBox28->Text, "I");
		}
		catch (System::IO::IOException^ ent) {
			worked = false;
			msgboxID = MessageBox::Show(
				this,
				"Helmholtz Coil not Connected\ncheck connection and try again",
				"Device Not Connected",
				MessageBoxButtons::OK
			);

		}
		if (worked) {
			label1->Text = System::Convert::ToString(i);
			if ((i % 2) == 0) {
				
			}

			}
		progressBar2->PerformStep();
	}
	int limEAN = helmdata.size();
	array<System::String^>^ helmdata2 = gcnew array<System::String^>(limEAN/2);
	j = 0;
	for (i = 0; i < limEAN; i+=2) {
		helmdata2[j] = msclr::interop::marshal_as<System::String^>(helmdata[i].substr(1, helmdata[i].size() - 7));
		chart1->Series[0]->Points->AddXY(j, std::stof(helmdata[i].substr(1, helmdata[i].size() - 8)));
		if (std::stof(helmdata[i].substr(1, helmdata[i].size() - 8)) > max) {
			max = std::stof(helmdata[i].substr(1, helmdata[i].size() - 8));
			maxint = i;
		}
		j++;
	}
	label1->Text= msclr::interop::marshal_as<System::String^>(helmdata[maxint].substr(1, helmdata[maxint].size() - 7));
	textBox30->Text = msclr::interop::marshal_as<System::String^>(helmdata[maxint].substr(1, helmdata[maxint].size()));
	textBox2->Lines = helmdata2;
	checkBox19->Checked = true;
}
private: System::Void progressBar1_Click(System::Object^ sender, System::EventArgs^ e) {
}
private: System::Void groupBox3_Enter(System::Object^ sender, System::EventArgs^ e) {
}
private: System::Void radioButton5_CheckedChanged(System::Object^ sender, System::EventArgs^ e) {
	button14->Visible = radioButton5->Checked;
}
private: System::Void button14_Click(System::Object^ sender, System::EventArgs^ e) {
	std::ofstream output1;
	std::string placeholder;
	System::String^ platecode;
	std::string suffix[12];
	System::Windows::Forms::DialogResult msgboxID;
	int i, imax,imin;
	time_t rawtime;
	char buffer[80];
	struct tm* timeinfo;
	//time_t timeinfo;
	if (textBox17->TextLength > 0) {
	time(&rawtime);
	placeholder = "1337";
	timeinfo = localtime(&rawtime);
	strftime(buffer, 80, " %F\t%T", timeinfo);
	suffix[0] = "-1"; suffix[1] = "-2"; suffix[2] = "-3"; suffix[3] = "-4";
	suffix[4] = "-1-1"; suffix[5] = "-2-1"; suffix[6] = "-3-1"; suffix[7] = "-4-1";
	suffix[8] = "-1-2"; suffix[9] = "-2-2"; suffix[10] = "-3-2"; suffix[11] = "-4-2";
	if (radioButton1->Checked) {
		platecode = "Y-";
		imax = 4;
		imin = 0;
	} else if (radioButton2->Checked) {
		platecode = textBox17->Text->Substring(0, 3);
		imin = 4;
		imax = 12;
	} else if(radioButton3->Checked) {
		platecode = textBox17->Text->Substring(0, 3);
		imin = 0;
		imax = 12;
	}
	for (i = imin; i < imax; i++) {
		if (i>=4){platecode="A"+ textBox17->Text->Substring(1, 2);
		}
		output1.open(msclr::interop::marshal_as<std::string>(textBox23->Text + platecode + textBox26->Text + msclr::interop::marshal_as <System::String^>(suffix[i])+ "_front.dat"), std::ios::app);
		output1 << buffer << '\t' << msclr::interop::marshal_as<std::string>(textBox24->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox25->Text) << '\t' << placeholder << '\t' << placeholder << '\t' << placeholder << '\t' << placeholder << '\n';
		output1.close();
		output1.open(msclr::interop::marshal_as<std::string>(textBox23->Text + platecode + textBox26->Text + msclr::interop::marshal_as <System::String^>( suffix[i]) + "_side.dat"), std::ios::app);
		output1 << buffer << '\t' << msclr::interop::marshal_as<std::string>(textBox24->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox25->Text) << '\t' << placeholder << '\t' << placeholder << '\t' << placeholder << '\t' << placeholder << '\n';
		output1.close();
		output1.open(msclr::interop::marshal_as<std::string>(textBox23->Text + platecode + textBox26->Text + msclr::interop::marshal_as <System::String^>( suffix[i]) + "_top.dat"), std::ios::app);
		output1 << buffer << '\t' << msclr::interop::marshal_as<std::string>(textBox24->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox25->Text) << '\t' << placeholder << '\t' << placeholder << '\t' << placeholder << '\t' << placeholder << '\n';
		output1.close();
		
		output1.open(msclr::interop::marshal_as<std::string>(textBox23->Text + platecode + textBox26->Text + msclr::interop::marshal_as <System::String^>(suffix[i]) + "_helmholtz.dat"), std::ios::app);
		output1 << buffer << '\t' << msclr::interop::marshal_as<std::string>(textBox24->Text) << '\t' << msclr::interop::marshal_as<std::string>(textBox25->Text) << '\t' << placeholder << ' ' << "nonunits" << '\n';
		output1.close();
		
	}
	textBox17->Text = "";
	textBox24->Text = "";
	textBox25->Text = "";
	textBox26->Text = "";
	textBox27->Text = "";
	readdos = false;
	readrod = false;
	readsam = false;
	radioButton1->Checked = false;
	radioButton2->Checked = false;
	radioButton3->Checked = false;
		}
		else {
			msgboxID = MessageBox::Show(
				this,
				"No Sample Number\nScan magnet barcode before proceeding",
				"No Sample Scanned",
				MessageBoxButtons::OK
			);
		}
}
private: System::Void label1_Click(System::Object^ sender, System::EventArgs^ e) {
}
private: System::Void button15_Click(System::Object^ sender, System::EventArgs^ e) {
	radioButton1->Checked = false;
	radioButton2->Checked = false;
	radioButton3->Checked = false;
	//textBox24->Text = "";
	//textBox25->Text = "";
	textBox26->Text = "";
	textBox27->Text = "";
	textBox17->Text = "";
	textBox4->Text = "";
	textBox5->Text = "";
	textBox6->Text = "";
	textBox7->Text = "";
	textBox8->Text = "";
	textBox9->Text = "";
	textBox10->Text = "";
	textBox11->Text = "";
	textBox12->Text = "";
	textBox13->Text = "";
	textBox14->Text = "";
	textBox15->Text = "";
	textBox16->Text = "";
	textBox30->Text = "";
	readdos = false;
	readrod = false;
	readsam = false;
	checkBox8->Checked = false;
	checkBox9->Checked = false;
	checkBox10->Checked = false;
	checkBox11->Checked = false;
	checkBox12->Checked = false;
	checkBox13->Checked = false;
	checkBox14->Checked = false;
	checkBox15->Checked = false;
	checkBox28->Checked = false;
	checkBox29->Checked = false;
	checkBox30->Checked = false;
	checkBox31->Checked = false;
	checkBox32->Checked = false;
	checkBox33->Checked = false;
	checkBox34->Checked = false;
	checkBox35->Checked = false;
	checkBox27->Checked = false;
	checkBox26->Checked = false;
	checkBox25->Checked = false;
	checkBox24->Checked = false;
	checkBox23->Checked = false;
	checkBox22->Checked = false;
	checkBox21->Checked = false;
	checkBox20->Checked = false;
}
private: System::Void textBox18_TextChanged(System::Object^ sender, System::EventArgs^ e) {
}
private: System::Void textBox17_TextChanged(System::Object^ sender, System::EventArgs^ e) {
}
};
}