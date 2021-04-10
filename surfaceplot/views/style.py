"""ウィジットのスタイル変更"""


def load_btn() -> str:
    """plotボタンのスタイル"""

    return 'background-color:orange;font-size:12pt;'


def tag(name: str, fontsize: int = None):
    """タグ装飾用デコレータ

    Parameters
    ----------
    name: str
        タグの名前
    fontsize: int default=None
        フォントサイズ
    """

    def _tag(f):
        def _wrapper(text: str):

            if fontsize is None:
                start_tag = f"<{name}>"
            else:
                start_tag = f"<{name} style='font-size:{fontsize}px;'>"

            body = f(text)
            end_tag = f"</{name}>"

            return start_tag + body + end_tag

        return _wrapper

    return _tag


@tag('div', 25)
def graph_title(text: str) -> str:
    return text


@tag('div', 18)
def data_label(text: str) -> str:
    return text
