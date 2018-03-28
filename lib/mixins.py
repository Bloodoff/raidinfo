import re


class TextAttributeParser(object):
    # (regexp, attr, default, accum, convert_func)
    _attributes = []

    def _set_default_attributes(self):
        for (_, attr, default, _, _) in self._attributes:
            if default is not None:
                setattr(self, attr, default)

    def _process_attributes_line(self, line, attributes_list=None):
        _attributes = self._attributes if attributes_list is None else attributes_list
        for (regexp, attr, default, accum, convert_func) in _attributes:
            match = re.search(regexp, line)
            if match:
                value = match.group(1) if (convert_func is None) else convert_func(match)
                if hasattr(self, attr) and accum:
                    setattr(self, attr, getattr(self, attr) + value)
                else:
                    setattr(self, attr, value)
                return True
        return False
