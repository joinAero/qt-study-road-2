.. _qstringlistmodel:

`43. QStringListModel <http://www.devbean.net/2013/02/qt-study-road-2-qstringlistmodel/>`_
==========================================================================================

:作者: 豆子

:日期: 2013年02月13日

上一章我们已经了解到有关 list、table 和 tree 三个最常用的视图类的便捷类的使用。前面也提到过，由于这些类仅仅是提供方便，功能、实现自然不如真正的 model/view 强大。从本章起，我们将了解最基本的 model/view 模型的使用。

既然是 model/view，我们也会分为两部分：model 和 view。本章我们将介绍 Qt 内置的最简单的一个模型：QStringListModel。接下来，我们再介绍另外的一些内置模型，在此基础上，我们将了解到 Qt 模型的基本架构，以便为最高级的应用——自定义模型——打下坚实的基础。


QStringListModel 是最简单的模型类，具备向视图提供字符串数据的能力。QStringListModel 是一个可编辑的模型，可以为组件提供一系列字符串作为数据。我们可以将其看作是封装了 QStringList 的模型。QStringList 是一种很常用的数据类型，实际上是一个字符串列表（也就是 QList<QString>）。既然是列表，它也就是线性的数据结构，因此，QStringListModel 很多时候都会作为 QListView 或者 QComboBox 这种只有一列的视图组件的数据模型。

下面我们通过一个例子来看看 QStringListModel 的使用。首先是我们的构造函数：

.. code-block:: c++

	MyListView::MyListView()
	{
	    QStringList data;
	    data << "Letter A" << "Letter B" << "Letter C";
	    model = new QStringListModel(this);
	    model->setStringList(data);
	 
	    listView = new QListView(this);
	    listView->setModel(model);
	 
	    QHBoxLayout *btnLayout = new QHBoxLayout;
	    QPushButton *insertBtn = new QPushButton(tr("insert"), this);
	    connect(insertBtn, SIGNAL(clicked()), this, SLOT(insertData()));
	    QPushButton *delBtn = new QPushButton(tr("Delete"), this);
	    connect(delBtn, SIGNAL(clicked()), this, SLOT(deleteData()));
	    QPushButton *showBtn = new QPushButton(tr("Show"), this);
	    connect(showBtn, SIGNAL(clicked()), this, SLOT(showData()));
	    btnLayout->addWidget(insertBtn);
	    btnLayout->addWidget(delBtn);
	    btnLayout->addWidget(showBtn);
	 
	    QVBoxLayout *mainLayout = new QVBoxLayout(this);
	    mainLayout->addWidget(listView);
	    mainLayout->addLayout(btnLayout);
	    setLayout(mainLayout);
	}

我们不贴出完整的头文件了，只看源代码文件。首先，我们创建了一个 QStringList 对象，向其中插入了几个数据；然后将其作为 QStringListModel 的底层数据。这样，我们可以理解为，QStringListModel 将 QStringList 包装了起来。剩下来的只是简单的界面代码，这里不再赘述。试运行一下，程序应该是这样的：

.. image:: imgs/43/qstringlistmodel-demo.png

接下来我们来看几个按钮的响应槽函数。

.. code-block:: c++

	void MyListView::insertData()
	{
	    bool isOK;
	    QString text = QInputDialog::getText(this, "Insert",
	                                         "Please input new data:",
	                                         QLineEdit::Normal,
	                                         "You are inserting new data.",
	                                         &isOK);
	    if (isOK) {
	        int row = listView->currentIndex().row();
	        model->insertRows(row, 1);
	        QModelIndex index = model->index(row);
	        model->setData(index, text);
	        listView->setCurrentIndex(index);
	        listView->edit(index);
	    }
	}

首先是 insertData() 函数。我们使用 QInputDialog::getText() 函数要求用户输入数据。这是 Qt 的标准对话框，用于获取用户输入的字符串。这部分在前面的章节中已经讲解过。当用户点击了 OK 按钮，我们使用 listView->currentIndex() 函数，获取 QListView 当前行。这个函数的返回值是一个 QModelIndex 类型。我们会在后面的章节详细讲解这个类，现在只要知道这个类保存了三个重要的数据：行索引、列索引以及该数据属于哪一个模型。我们调用其 row() 函数获得行索引，该返回值是一个 int，也就是当前是第几行。然后我们向模型插入新的一行。insertRows() 函数签名如下：

.. code-block:: c++

	bool insertRows(int row, int count, const QModelIndex &parent = QModelIndex());

该函数会将 count 行插入到模型给定的 row 的位置，新行的数据将会作为 parent 的子元素。如果 row 为 0，新行将被插入到 parent 的原有数据之前，否则将在已有数据之后。如果 parent 没有子元素，则会新插入一个单列数据。函数插入成功返回 true，否则返回 false。我们在这段代码中调用的是 insertRows(row, 1)。这是 QStringListModel 的一个重载。参数 1 说明要插入 1 条数据。记得之前我们已经把 row 设置为当前行，因此，这行语句实际上是在当前的 row 位置插入 count 行，这里的 count 为 1。由于我们没有添加任何数据，实际效果是，我们在 row 位置插入了 1 个空行。然后我们使用 model 的 index() 函数获取当前行的 QModelIndex 对象，利用 setData() 函数把我们用 QInputDialog 接受的数据设置为当前行数据。接下来，我们使用 setCurrentIndex() 函数，把当前行设为新插入的一行，并调用 edit() 函数，使这一行可以被编辑。

以上是我们提供的一种插入数据的方法：首先插入空行，然后选中新插入的空行，设置新的数据。这其实是一种冗余操作，因为 currentIndex() 已经获取到当前行。在此，我们仅仅是为了介绍这些函数的使用。因此，除去这些冗余，我们可以使用一种更简洁的写法：

.. code-block:: c++

	void MyListView::insertData()
	{
	    bool isOK;
	    QString text = QInputDialog::getText(this, "Insert",
	                                         "Please input new data:",
	                                         QLineEdit::Normal,
	                                         "You are inserting new data.",
	                                         &isOK);
	    if (isOK) {
	        QModelIndex currIndex = listView->currentIndex();
	        model->insertRows(currIndex.row(), 1);
	        model->setData(currIndex, text);
	        listView->edit(currIndex);
	    }
	}

接下来是删除数据：

.. code-block:: c++

	void MyListView::deleteData()
	{
	    if (model->rowCount() > 1) {
	        model->removeRows(listView->currentIndex().row(), 1);
	    }
	}

使用模型的 removeRows() 函数可以轻松完成这个操作。这个函数同前面所说的 insertRows() 很类似，这里不再赘述。需要注意的是，我们用 rowCount() 函数判断了一下，要求最终始终保留 1 行。这是因为我们写的简单地插入操作所限制，如果把数据全部删除，就不能再插入数据了。所以，前面所说的插入操作实际上还需要再详细考虑才可以解决这一问题。

最后是简单地将所有数据都显示出来：

.. code-block:: c++

	void MyListView::showData()
	{
	    QStringList data = model->stringList();
	    QString str;
	    foreach(QString s, data) {
	        str += s + "\n";
	    }
	    QMessageBox::information(this, "Data", str);
	}

这段代码没什么好说的。

关于 QStringListModel 我们简单介绍这些。从这些示例中可以看到，几乎所有操作都是针对模型的，也就是说，我们直接对数据进行操作，当模型检测到数据发生了变化，会立刻通知视图进行刷新。这样，我们就可以把精力集中到对数据的操作上，而不用担心视图的同步显示问题。这正是 model/view 模型所带来的一个便捷之处。
