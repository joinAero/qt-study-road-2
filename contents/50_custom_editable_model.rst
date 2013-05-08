.. _custom_editable_model:

`50. 自定义可编辑模型 <http://www.devbean.net/2013/05/qt-study-road-2-custom-editable-model/>`_
===============================================================================================

:作者: 豆子

:日期: 2013年05月13日

上一章我们了解了如何自定义只读模型。顾名思义，只读模型只能够用于展示只读数据，用户不能对其进行修改。如果允许用户修改数据，则应该提供可编译的模型。可编辑模型与只读模型非常相似，至少在展示数据方面几乎是完全一样的，所不同的是可编译模型需要提供用户编辑数据后，应当如何将数据保存到实际存储值中。


我们还是利用上一章的 CurrencyModel，在此基础上进行修改。相同的代码这里不再赘述，我们只列出增加以及修改的代码。相比只读模型，可编辑模型需要增加以下两个函数的实现：

.. code-block:: c++

    Qt::ItemFlags flags(const QModelIndex &index) const;
    bool setData(const QModelIndex &index, const QVariant &value,
                 int role = Qt::EditRole);

还记得之前我们曾经介绍过，在 Qt 的 model/view 模型中，我们使用委托 delegate 来实现数据的编辑。在实际创建编辑器之前，委托需要检测这个数据项是不是允许编辑。模型必须让委托知道这一点，这是通过返回模型中每个数据项的标记 flag 来实现的，也就是这个 flags() 函数。这本例中，只有行和列的索引不一致的时候，我们才允许修改（因为对角线上面的值恒为 1.0000，不应该对其进行修改）：

.. code-block:: c++

    Qt::ItemFlags CurrencyModel::flags(const QModelIndex &index) const
    {
        Qt::ItemFlags flags = QAbstractItemModel::flags(index);
        if (index.row() != index.column()) {
            flags |= Qt::ItemIsEditable;
        }
        return flags;
    }

注意，我们并不是在判断了 index.row() != index.column() 之后直接返回 Qt::ItemIsEditable，而是返回 QAbstractItemModel::flags(index) | Qt::ItemIsEditable。这是因为我们不希望丢弃原来已经存在的那些标记。

我们不需要知道在实际编辑的过程中，委托究竟做了什么，只需要提供一种方式，告诉 Qt 如何将委托获得的用户输入的新的数据保存到模型中。这一步骤是通过 setData() 函数实现的：

.. code-block:: c++

    bool CurrencyModel::setData(const QModelIndex &index,
                                const QVariant &value, int role)
    {
        if (index.isValid()
                && index.row() != index.column()
                && role == Qt::EditRole) {
            QString columnCurrency = headerData(index.column(),
                                                Qt::Horizontal, Qt::DisplayRole)
                                         .toString();
            QString rowCurrency = headerData(index.row(),
                                             Qt::Vertical, Qt::DisplayRole)
                                      .toString();
            currencyMap.insert(columnCurrency,
                               value.toDouble() * currencyMap.value(rowCurrency));
            emit dataChanged(index, index);
            return true;
        }
        return false;
    }

回忆一下我们的业务逻辑：我们的底层数据结构中保存的是各个币种相对美元的汇率，显示的时候，我们使用列与行的比值获取两两之间的汇率。例如，当我们修改 currencyMap["CNY"]/currencyMap["HKD"] 的值时，我们认为人民币相对美元的汇率发生了变化，而港币相对美元的汇率保持不变，因此新的数值应当是用户新输入的值与原来 currencyMap["HKD"] 的乘积。这正是上面的代码所实现的逻辑。另外注意，在实际修改之前，我们需要检查 index 是否有效，以及从业务来说，行列是否不等，最后还要检查角色是不是 Qt::EditRole。这里为方便起见，我们使用了 Qt::EditRole，也就是编辑时的角色。但是，对于布尔类型，我们也可以选择使用设置 Qt::ItemIsUserCheckable 标记的 Qt::CheckStateRole，此时，Qt 会显示一个选择框而不是输入框。注意这里的底层数据都是一样的，只不过显示方式的区别。当数据重新设置是，模型必须通知视图，数据发生了变化。这要求我们必须发出 dataChanged() 信号。由于我们只有一个数据发生了改变，因此这个信号的两个参数是一致的（dataChanged() 的两个参数是发生改变的数据区域的左上角和右下角的索引值，由于我们只改变了一个单元格，所以二者是相同的）。最后，如果数据修改成功就返回 true，否则返回 false。

当我们完成以上工作时，还需要修改一下 data() 函数：

.. code-block:: c++

    QVariant CurrencyModel::data(const QModelIndex &index, int role) const
    {
        if (!index.isValid()) {
            return QVariant();
        }
     
        if (role == Qt::TextAlignmentRole) {
            return int(Qt::AlignRight | Qt::AlignVCenter);
        } else if (role == Qt::DisplayRole || role == Qt::EditRole) {
            QString rowCurrency = currencyAt(index.row());
            QString columnCurrency = currencyAt(index.column());
            if (currencyMap.value(rowCurrency) == 0.0) {
                return "####";
            }
            double amount = currencyMap.value(columnCurrency)
                                / currencyMap.value(rowCurrency);
            return QString("%1").arg(amount, 0, 'f', 4);
        }
        return QVariant();
    }

我们的修改很简单：仅仅是增加了 role == Qt::EditRole 这么一行判断。这意味着，当是 EditRole 时，Qt 会提供一个默认值。我们可以试着删除这个判断来看看其产生的效果。

最后运行一下程序，修改一下数据就会发现，当我们修改过一个单元格后，Qt 会自动刷新所有受影响的数据的值。这也正是 model / view 模型的强大之处：对数据模型的修改会直接反映到视图上。
