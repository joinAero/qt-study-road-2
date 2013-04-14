.. _binary_file_io:

`36. 二进制文件读写 <http://www.devbean.net/2013/01/qt-study-road-2-binary-file-io/>`_
======================================================================================

:作者: 豆子

:日期: 2013年01月06日

在上一章中，我们介绍了有关 QFile 和 QFileInfo 两个类的使用。我们提到，QIODevice 提供了 read()、readLine() 等基本的操作。同时，Qt 还提供了更高一级的操作：用于二进制的流 QDataStream 和用于文本流的 QTextStream。本节，我们将讲解有关 QDataStream 的使用以及一些技巧。下一章则是 QTextStream 的相关内容。

QDataStream 提供了基于 QIODevice 的二进制数据的序列化。数据流是一种二进制流，这种流 **完全不依赖** 于底层操作系统、CPU 或者字节顺序（大端或小端）。例如，在安装了 Windows 平台的 PC 上面写入的一个数据流，可以不经过任何处理，直接拿到运行了 Solaris 的 SPARC 机器上读取。由于数据流就是二进制流，因此我们也可以直接读写没有变吗的二进制数据，例如图像、视频、音频等。

QDataStream 既能够存取 C++ 基本类型，如 int、char、short 等，也可以存取复杂的数据类型，例如自定义的类。实际上，QDataStream 对于类的存储，是将复杂的类分割为很多基本单元实现的。

结合 QIODevice，QDataStream 可以很方便地对文件、网络套接字等进行读写操作。我们从代码开始看起：

.. code-block:: c++

	QFile file("file.dat");
	file.open(QIODevice::WriteOnly);
	QDataStream out(&file);
	out << QString("the answer is");
	out << (qint32)42;

在这段代码中，我们首先打开一个名为 file.dat 的文件（注意，我们为简单起见，并没有检查文件打开是否成功，这在正式程序中是不允许的）。然后，我们将刚刚创建的 file 对象的指针传递给一个 QDataStream 实例 out。类似于 std::cout 标准输出流，QDataStream 也重载了输出重定向 << 运算符。后面的代码就很简单了：将“the answer is”和数字 42 输出到数据流（如果你不明白这句话的意思，这可是宇宙终极问题的答案 ;-P 请自行搜索《银河系漫游指南》）。由于我们的 out 对象建立在 file 之上，因此相当于将宇宙终极问题的答案写入 file。

需要指出一点：最好使用 Qt 整型来进行读写，比如程序中的 qint32。这保证了在任意平台和任意编译器都能够有相同的行为。

我们通过一个例子来看看 Qt 是如何存储数据的。例如 char * 字符串，在存储时，会首先存储该字符串包括 \0 结束符的长度（32位整型），然后是字符串的内容以及结束符 \0。在读取时，先以 32 位整型读出整个的长度，然后按照这个长度取出整个字符串的内容。

但是，如果你直接运行这段代码，你会得到一个空白的 file.dat，并没有写入任何数据。这是因为我们的 file 没有正常关闭。为性能起见，数据只有在文件关闭时才会真正写入。因此，我们必须在最后添加一行代码：

.. code-block:: c++

	file.close(); // 如果不想关闭文件，可以使用 file.flush();

重新运行一下程序，你就得到宇宙终极问题的答案了。

我们已经获得宇宙终极问题的答案了，下面，我们要将这个答案读取出来：

.. code-block:: c++

	QFile file("file.dat");
	file.open(QIODevice::ReadOnly);
	QDataStream in(&file);
	QString str;
	qint32 a;
	in >> str >> a;

这段代码没什么好说的。唯一需要注意的是，你必须按照写入的顺序，将数据读取出来。也就是说，程序数据写入的顺序必须预先定义好。在这个例子中，我们首先写入字符串，然后写入数字，那么就首先读出来的就是字符串，然后才是数字。顺序颠倒的话，程序行为是不确定的，严重时会直接造成程序崩溃。

由于二进制流是纯粹的字节数据，带来的问题是，如果程序不同版本之间按照不同的方式读取（前面说过，Qt 保证读写内容的一致，但是并不能保证不同 Qt 版本之间的一致），数据就会出现错误。因此，我们必须提供一种机制来确保不同版本之间的一致性。通常，我们会使用如下的代码写入：

.. code-block:: c++

	QFile file("file.dat");
	file.open(QIODevice::WriteOnly);
	QDataStream out(&file);
	 
	// 写入魔术数字和版本
	out << (quint32)0xA0B0C0D0;
	out << (qint32)123;
	 
	out.setVersion(QDataStream::Qt_4_0);
	 
	// 写入数据
	out << lots_of_interesting_data;

这里，我们增加了两行代码：

.. code-block:: c++

	out << (quint32)0xA0B0C0D0;

用于写入魔术数字。所谓魔术数字，是二进制输出中经常使用的一种技术。二进制格式是人不可读的，并且通常具有相同的后缀名（比如 dat 之类），因此我们没有办法区分两个二进制文件哪个是合法的。所以，我们定义的二进制格式通常具有一个魔术数字，用于标识文件的合法性。在本例中，我们在文件最开始写入 0xA0B0C0D0，在读取的时候首先检查这个数字是不是 0xA0B0C0D0。如果不是的话，说明这个文件不是可识别格式，因此根本不需要去继续读取。一般二进制文件都会有这么一个魔术数字，例如 Java 的 class 文件的魔术数字就是 0xCAFEBABE，使用二进制查看器就可以查看。魔术数字是一个 32 位的无符号整型，因此我们使用 quint32 来得到一个平台无关的 32 位无符号整型。

接下来一行，

.. code-block:: c++

	out << (qint32)123;

是标识文件的版本。我们用魔术数字标识文件的类型，从而判断文件是不是合法的。但是，文件的不同版本之间也可能存在差异：我们可能在第一版保存整型，第二版可能保存字符串。为了标识不同的版本，我们只能将版本写入文件。比如，现在我们的版本是 123。

下面一行还是有关版本的：

.. code-block:: c++

	out.setVersion(QDataStream::Qt_4_0);

上面一句是文件的版本号，但是，Qt 不同版本之间的读取方式可能也不一样。这样，我们就得指定 Qt 按照哪个版本去读。这里，我们指定以 Qt 4.0 格式去读取内容。

当我们这样写入文件之后，我们在读取的时候就需要增加一系列的判断：

.. code-block:: c++

	QFile file("file.dat");
	file.open(QIODevice::ReadOnly);
	QDataStream in(&file);
	 
	// 检查魔术数字
	quint32 magic;
	in >> magic;
	if (magic != 0xA0B0C0D0) {
	    return BAD_FILE_FORMAT;
	}
	 
	// 检查版本
	qint32 version;
	in >> version;
	if (version < 100) {
	    return BAD_FILE_TOO_OLD;
	}
	if (version > 123) {
	    return BAD_FILE_TOO_NEW;
	}
	 
	if (version <= 110) {
	    in.setVersion(QDataStream::Qt_3_2);
	} else {
	    in.setVersion(QDataStream::Qt_4_0);
	}
	// 读取数据
	in >> lots_of_interesting_data;
	if (version >= 120) {
	    in >> data_new_in_version_1_2;
	}
	in >> other_interesting_data;

这段代码就是按照前面的解释进行的。首先读取魔术数字，检查文件是否合法。如果合法，读取文件版本：小于 100 或者大于 123 都是不支持的。如果在支持的版本范围内（100 <= version <= 123），则当是小于等于 110 的时候，按照 Qt_3_2 的格式读取，否则按照 Qt_4_0 的格式读取。当设置完这些参数之后，开始读取数据。

至此，我们介绍了有关 QDataStream 的相关内容。那么，既然 QIODevice 提供了 read()、readLine() 之类的函数，为什么还要有 QDataStream 呢？QDataStream 同 QIODevice 有什么区别？区别在于，有些 QIODevice 支持随机读写，而 QDataStream 提供的是流的形式，不允许随机读写。我们通过下面一段代码看看什么是流的形式：

.. code-block:: c++

	QFile file("file.dat");
	file.open(QIODevice::ReadWrite);
	 
	QDataStream stream(&file);
	QString str = "the answer is 42";
	QString strout;
	 
	stream << str;
	file.flush();
	stream >> strout;

在这段代码中，我们首先向文件中写入数据，紧接着把数据读出来。有什么问题吗？运行之后你会发现，strout 实际是空的。为什么没有读取出来？我们不是已经添加了 file.flush(); 语句吗？原因并不在于文件有没有写入，而是在于我们使用的是“流”。所谓流，就像水流一样，它的游标会随着输出向后移动。当使用 << 操作符输出之后，流的游标已经到了最后，此时你再去读，当然什么也读不到了。所以你需要在输出之后重新把游标设置为 0 的位置才能够继续读取。具体代码片段如下：

.. code-block:: c++

	stream << str;
	stream.device()->seek(0);
	stream >> strout;
