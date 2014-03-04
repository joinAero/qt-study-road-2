.. _do_while_in_macro:

`宏定义中的 do {…} while (0) <http://www.devbean.net/2014/01/do-while-in-macro/>`_
===================================================================================

:作者: 豆子

:日期: 2014年01月28日

参考链接：http://www.pixelstech.net/article/1390482950-do-%7B-%7D-while-%280%29-in-macros

虽然我们不建议使用宏，但是，作为一个语言特性，有时宏是不可避免的。对于这种情况，正确使用宏尤其重要。它可以帮助你减少很多重复性工作。但是，如果你没有仔细地定义，宏绝对能把你逼疯。在很多 C/C++ 程序中，你会看到类似如下定义的宏：

.. code-block:: c++

    #define __set_task_state(tsk, state_value)      \
        do { (tsk)->state = (state_value); } while (0)

宏的语句被do{...}while(0)包围起来。在很多 C 库，包括 Linux 内核中，这种情形都不少见。这种红如何使用？来自 Google 的 Robert Love（他曾经是 Linux 内核开发人员）给了我们答案。

do{...}while(0)是 C 语言中唯一能让宏后面加上分号还能够正确工作的语法结构。使用do{...}while(0)包围起来，我们就不需要担心宏被如何使用。例如：

.. code-block:: c++

    #define foo(x)  bar(x); baz(x)

之后，我们这样调用：

.. code-block:: c++

    foo(wolf);

宏将被展开为

.. code-block:: c++

    bar(wolf); baz(wolf);

这正是正确的结果。下面，我们来看另外一种情况：

.. code-block:: c++

    if (!feral)
        foo(wolf);

此时，宏展开结果为：

.. code-block:: c++

    if (!feral)
        bar(wolf);
    baz(wolf);

这很可能不是你所期望的。

也就是说，我们所定义的这个宏并不适用于所有使用它的情形。没有do{...}while(0)语句，我们不可能写出类似函数的宏。

如果我们将这个宏使用do{...}while(0)语句重新定义，那么就会是这样的：

.. code-block:: c++

    #define foo(x)  do { bar(x); baz(x); } while (0)

现在，这个语句与之前的那个在功能上是等价的。通过将语句嵌于花括号之内，我们保证了整个逻辑不会被宏外面的分号打断；while(0)则保证这个逻辑片段只执行一次，这和没有循环是一致的。使用改进过的宏，上述语句会被展开为：

.. code-block:: c++

    if (!feral)
        do { bar(wolf); baz(wolf); } while (0);

语义上说，它等价于：

.. code-block:: c++

    if (!feral) {
        bar(wolf);
        baz(wolf);
    }

或许你会问，为什么不仅仅使用一对花括号就好了？为什么必须要有do{...}while(0)？例如，我们这样定义宏：

.. code-block:: c++

    #define foo(x)  { bar(x); baz(x); }

如此定义，上面的展开语句仍然正确。但是，我们考虑另外一种情况：

.. code-block:: c++

    if (!feral)
        foo(wolf);
    else
        bin(wolf);

这种写法将被展开为：

.. code-block:: c++

    if (!feral) {
        bar(wolf);
        baz(wolf);
    };
    else
        bin(wolf);

现在我们有了一个语法错误。

总结一下，在 Linux 或其它代码库中的宏使用do{...}while(0)包围其逻辑，这保证了宏在使用时，不管宏所在的位置花括号、分号如何写，宏的表现总是一致的。