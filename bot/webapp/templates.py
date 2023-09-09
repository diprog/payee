import io

from lxml import etree

# Путь к HTML-шаблонам в проекте
html_path = 'bot/webapp/html/'


def parse_html(path) -> etree.ElementTree:
    """
    Читает HTML-файл и возвращает его в виде объекта дерева элементов.

    :param path: Путь к HTML-файлу.
    :return: Объект дерева элементов.
    """
    with open(html_path + path, 'rb') as f:
        # Чтение файла и преобразование его в дерево элементов
        return etree.parse(io.BytesIO(f.read()), etree.HTMLParser(encoding='utf-8'))


def read_html(path) -> str:
    """
    Читает HTML-файл и возвращает его содержимое в виде строки.

    :param path: Путь к HTML-файлу.
    :return: Содержимое файла в виде строки.
    """
    with open(html_path + path, 'r', encoding='utf-8') as f:
        # Чтение содержимого файла
        return f.read()


def load_from_base_template(path) -> str:
    """
    Загружает содержимое HTML-файла и подставляет его в базовый шаблон.

    :param path: Путь к HTML-файлу.
    :return: Строка с HTML-кодом, где содержимое файла вставлено в базовый шаблон.
    """
    # Чтение базового шаблона и HTML-файла
    base_tempalte = read_html('_base_template.html')
    html = read_html(path)

    # Извлечение содержимого тегов <body> и <script> из HTML-файла
    body_content_str = html.split('<body>')[-1].split('</body>')[0]
    script_str = html.split('<script>')[-1].split('</script>')[0]

    # Вставка содержимого тегов <body> и <script> в базовый шаблон и возвращение результата
    return (
        base_tempalte
        .replace('<section>\n</section>', body_content_str)
        .replace('// INSERT SCRIPT HERE (this line is for templates.py)', script_str)
    )
