.. _qml_component:

`79. QML 组件 <http://www.devbean.net/2014/01/qt-study-road-2-qml-component/>`_
===============================================================================

:作者: 豆子

:日期: 2014年01月19日

前面我们简单介绍了几种 QML 的基本元素。QML 可以由这些基本元素组合成一个复杂的元素，方便以后我们的重用。这种组合元素就被称为组件。组件就是一种可重用的元素。QML 提供了很多方法来创建组件。不过，本章我们只介绍一种方式：基于文件的组件。基于文件的组件将 QML 元素放置在一个单独的文件中，然后给这个文件一个名字。以后我们就可以通过这个名字来使用这个组件。例如，如果有一个文件名为 Button.qml，那么，我们就可以在 QML 中使用Button { … }这种形式。

下面我们通过一个例子来演示这种方法。我们要创建一个带有文本说明的Rectangle，这个矩形将成为一个按钮。用户可以点击矩形来响应事件。

.. code-block:: javascript

    import QtQuick 2.0

    Rectangle {
        id: root

        property alias text: label.text
        signal clicked

        width: 116; height: 26
        color: "lightsteelblue"
        border.color: "slategrey"

        Text {
            id: label
            anchors.centerIn: parent
            text: "Start"
        }
        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.clicked()
            }
        }
    }

我们将这个文件命名为 Button.qml，放在 main.qml 同一目录下。这里的 main.qml 就是 IDE 帮我们生成的 QML 文件。此时，我们已经创建了一个 QML 组件。这个组件其实就是一个预定义好的Rectangle。这是一个按钮，有一个Text用于显示按钮的文本；有一个MouseArea用于接收鼠标事件。用户可以定义按钮的文本，这是用过设置Text的text属性实现的。为了不对外暴露Text元素，我们给了它的text属性一个别名。signal clicked给这个Button一个信号。由于这个信号是无参数的，我们也可以写成signal clicked()，二者是等价的。注意，这个信号会在MouseArea的clicked信号被发出，具体就是在MouseArea的onClicked属性中调用个这个信号。

下面我们需要修改 main.qml 来使用这个组件：

.. code-block:: javascript

    import QtQuick 2.0

    Rectangle {
        width: 360
        height: 360
        Button {
            id: button
            x: 12; y: 12
            text: "Start"
            onClicked: {
                status.text = "Button clicked!"
            }
        }

        Text {
            id: status
            x: 12; y: 76
            width: 116; height: 26
            text: "waiting ..."
            horizontalAlignment: Text.AlignHCenter
        }
    }

在 main.qml 中，我们直接使用了Button这个组件，就像 QML 其它元素一样。由于 Button.qml 与 main.qml 位于同一目录下，所以不需要额外的操作。但是，如果我们将 Button.qml 放在不同目录，比如构成如下的目录结果：

.. code-block:: none

    app
     |- QML
     |   |- main.qml
     |- components
         |- Button.qml

那么，我们就需要在 main.qml 的import部分增加一行import ../components才能够找到Button组件。

有时候，选择一个组件的根元素很重要。比如我们的Button组件。我们使用Rectangle作为其根元素。Rectangle元素可以设置背景色等。但是，有时候我们并不允许用户设置背景色。所以，我们可以选择使用Item元素作为根。事实上，Item元素作为根元素会更常见一些。