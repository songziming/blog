title: 使用 Open XML SDK 创建 Word 文档
category: default
tags:
- office
---

微软最近开源了 Open XML SDK，它可以创建符合 Open XML 规范的文档，如 docx、xlsx、pptx。虽然 SDK 本身是 C# 语言编写的，但幸好有 Mono，我们也可以在 Linux 下使用这个工具创建 Word 文档。

### 编译 SDK

首先，获取 Open XML SDK 的源代码：

``` bash
git clone https://github.com/OfficeDev/Open-XML-SDK
```

进入源码目录，会发现其中有一个名为 `Makefile-Linux-Mono` 的文件，使用下面的命令进行编译：

``` bash
make -f Makefile-Linux-Mono build
```

编译完成后，便可以在 `build/OpenXmlSdkLib` 目录下找到所需的 DLL 文件。

### 使用 SDK

有了 DLL 文件，就可以将其用在 C# 工程中。Open XML SDK 使用了 System.Package API，因此引用 SDK 的同时还需要引用 WindowsBase。如果使用 Mono 编译器，可以使用编译参数 `-r:WindowsBase,OpenXMLLib` 来引用依赖项（需要保证 `OpenXMLLib.dll` 文件位于当前目录中）。

为了方便起见，也可以使用 MonoDevelop IDE。向工程的 References 中添加 `WindowsBase` 和 `OpenXMLLib.dll` 即可。

### DOCX 文件结构

DOCX 文件实际上是一个 Zip 压缩包，如果将文件后缀改为 `.zip` 就可以解压并看到其内容，基本都是 
XML文件。其中 `word` 目录下的文件是文档的主要部分，包括文档主体内容（`document.xml`）、样式定义（`styles.xml`）、页眉页脚（`header.xml` 和 `footer.xml`）等。

docx 文件使用的 XML 也称作 WordprocessingML，在 SDK 中有相应的类进行封装。

### 创建一个文档

之前说过，一个 docx 文件是一个压缩包，其中包含许多部分。`WordprocessingDocuemnt` 类表示一个 docx 文件，要创建一个最简单的 Word 文档，只需要使用下面的代码：

``` csharp
using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;

public class Sample {
    public static void Main(string[] args) {
        WordprocessingDocument package =
            WordprocessingDocument.Create("output.docx", WordprocessingDocumentType.Document);
        MainDocumentPart mainPart = package.AddMainDocumentPart();
        mainPart.Document = new Document(
            new Body(
            new Paragraph(
            new Run(
            new Text("Hello, world!");
        ))));
        mainPart.Document.Save();
    }
}
```

编译运行上面的代码，会在当前目录下生成一个 `output.docx` 文件，打开之后可以看到内容 “Hello, world!”。

从上面的例子可以看出一个 Word 文档的基本层次结构。最外层是一个 `WordprocessingDocument`，里面包含一个 `MainDocumentPart`，里面有一个 `Document`，在下面依次是 `Body`、`Paragraph`、`Run`、`Text`。

### 基本方法

SDK 中多数类都有其对应的 XML 元素。XML 是一个具有层级关系的文件结构，每个元素都可以包含其他元素，因此 Open XML SDK 中也体现了这种特点（个人认为，SDK 对 Open XML 的封装非常原始）。`Document`、`Body`、`Paragraph`、`Run` 和 `Text` 这些类都有一个 Append 方法，可以向对应的 XML 元素内部添加子元素。XML 元素的属性通过 C# 对象的属性器进行访问和修改。

- - -

### Paragraph

顾名思义，Paragraph 表示一个段落。Paragraph 可以包含属性，用 ParagraphProperties 类来表示，但 ParagraphProperties 只有作为 Paragraph 的第一个子元素时才有效。

### Section

OOXML 并没有规定纸张参数，但是在 Word 中也可以设置纸张尺寸、方向和页边距等信息，而且一个文档还可以使用多种纸型，这是用过 Section 实现的。将一个文档划分为若干 Section，每个 Section 包含若干 Paragraph，这些 Paragraph 有共同的纸张大小、方向、边距
