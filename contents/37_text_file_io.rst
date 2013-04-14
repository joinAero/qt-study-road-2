.. _text_file_io:

`37. 文本文件读写 <http://www.devbean.net/2013/01/qt-study-road-2-text-file-io/>`_
==================================================================================

:作者: 豆子

:日期: 2013年01月07日

上一章我们介绍了有关二进制文件的读写。二进制文件比较小巧，却不是人可读的格式。而文本文件是一种人可读的文件。为了操作这种文件，我们需要使用 QTextStream 类。QTextStream 和 QDataStream 的使用类似，只不过它是操作纯文本文件的。另外，像 XML、HTML 这种，虽然也是文本文件，可以由 QTextStream 生成，但 Qt 提供了更方便的 XML 操作类，这里就不包括这部分内容了。

QTextStream 会自动将 Unicode 编码同操作系统的编码进行转换，这一操作对开发人员是透明的。它也会将换行符进行转换，同样不需要自己处理。QTextStream 使用 16 位的 QChar 作为基础的数据存储单位，同样，它也支持 C++ 标准类型，如 int 等。实际上，这是将这种标准类型与字符串进行了相互转换。


QTextStream 同 QDataStream 的使用基本一致，例如下面的代码将把“The answer is 42”写入到 file.txt 文件中：

.. code-block:: c++

	QFile data("file.txt");
	if (data.open(QFile::WriteOnly | QIODevice::Truncate)) {
	    QTextStream out(&data);
	    out << "The answer is " << 42;
	}

这里，我们在 open() 函数中增加了 QIODevice::Truncate 打开方式。我们可以从下表中看到这些打开方式的区别：

=====================	=====================
枚举值					描述
=====================	=====================
QIODevice::NotOpen		未打开
QIODevice::ReadOnly		以只读方式打开
QIODevice::WriteOnly	以只写方式打开
QIODevice::ReadWrite	以读写方式打开
QIODevice::Append		以追加的方式打开，新增加的内容将被追加到文件末尾
QIODevice::Truncate		以重写的方式打开，在写入新的数据时会将游标设置在文件开头
QIODevice::Text			在读取时，将行结束符转换成 \n；在写入时，将行结束符转换成本地格式，例如 Win32 平台上是 \r\n
QIODevice::Unbuffered	忽略缓存
=====================	=====================

我们在这里使用了 QFile::WriteOnly | QIODevice::Truncate，也就是以只写并且覆盖已有内容的形式操作文件。注意，QIODevice::Truncate 并不是将文件内容清空，而是在文件开头处开始写入。要理解这一点，假设原文件内容是1111111111，我们想要写入222，如果设置为 QIODevice::Append，则处理结果将会是 1111111111222，这是很容易理解的；如果设置为 QIODevice::Truncate，那么文件内容将会是 2221111111。

虽然 QTextStream 的写入内容与 QDataStream 一直，但是读取时却会有些困难：

.. code-block:: c++

	QFile data("file.txt");
	if (data.open(QFile::ReadOnly)) {
	    QTextStream in(&data);
	    QString str;
	    int ans = 0;
	    in >> str >> ans;
	}

在使用 QDataStream 的时候，这样的代码很方便，但是使用了 QTextStream 时却有所不同：读出的时候，str 里面将是 The answer is 42，ans 是 0。这是因为以文本形式写入数据，是没有数据之间的分隔的。还记得我们前面曾经说过，使用 QDataStream 写入的时候，实际上会在要写入的内容前面，额外添加一个这段内容的长度值。而文本文件则没有类似的操作。因此，使用文本文件时，很少会将其分割开来读取，而是使用诸如 QTextStream::readLine() 读取一行，使用 QTextStream::readAll() 读取所有文本这种函数，之后再对获得的 QString 对象进行处理。

默认情况下，QTextStream 的编码格式是 Unicode，如果我们需要使用另外的编码，可以使用

.. code-block:: c++

	stream.setCodec("UTF-8");

这样的函数进行设置。

另外，为方便起见，QTextStream 同 std::cout 一样提供了很多描述符，被称为 stream manipulators。因为文本文件是供人去读的，自然需要良好的格式（相比而言，二进制文件就没有这些问题，只要数据准确就可以了）。这些描述符是一些函数的简写，我们可以从文档中找到：

=============== ===============
描述符			等价于
=============== ===============
bin				setIntegerBase(2)
oct				setIntegerBase(8)
dec				setIntegerBase(10)
hex				setIntegerBase(16)
showbase		setNumberFlags(numberFlags() | ShowBase)
forcesign		setNumberFlags(numberFlags() | ForceSign)
forcepoint		setNumberFlags(numberFlags() | ForcePoint)
noshowbase		setNumberFlags(numberFlags() & ~ShowBase)
noforcesign		setNumberFlags(numberFlags() & ~ForceSign)
noforcepoint	setNumberFlags(numberFlags() & ~ForcePoint)
uppercasebase	setNumberFlags(numberFlags() | UppercaseBase)
uppercasedigits	setNumberFlags(numberFlags() | UppercaseDigits)
lowercasebase	setNumberFlags(numberFlags() & ~UppercaseBase)
lowercasedigits	setNumberFlags(numberFlags() & ~UppercaseDigits)
fixed			setRealNumberNotation(FixedNotation)
scientific		setRealNumberNotation(ScientificNotation)
left			setFieldAlignment(AlignLeft)
right			setFieldAlignment(AlignRight)
center			setFieldAlignment(AlignCenter)
endl			operator<<(‘\n’) and flush()
flush			flush()
reset			reset()
ws				skipWhiteSpace()
bom				setGenerateByteOrderMark(true)
=============== ===============

这些描述符只是一些函数的简写。例如，我们想要输出 12345678 的二进制形式，那么可以直接使用

.. code-block:: c++

	out << bin << 12345678;

就可以了。这等价于

.. code-block:: c++

	out.setIntegerBase(2);
	out << 12345678;

更复杂的，如果我们想要舒服 1234567890 的带有前缀、全部字母大写的十六进制格式（0xBC614E），那么只要使用

.. code-block:: c++

	out << showbase << uppercasedigits << hex << 12345678;

即可。

不仅是 QIODevice，QTextStream 也可以直接把内容输出到 QString。例如

.. code-block:: c++

	QString str;  
	QTextStream(&str) << oct << 31 << " " << dec << 25 << endl;

这提供了一种简单的处理字符串内容的方法。
