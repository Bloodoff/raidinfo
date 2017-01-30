import re


class TextAttributeParser(object):
    # (regexp, attr, default, convert_func)
    _attributes = []

    def _set_default_attributes(self):
        for (regexp, attr, default, convert_func) in self._attributes:
            if default is not None:
                setattr(self, attr, default)

    def _process_attributes_line(self, line):
        for (regexp, attr, default, convert_func) in self._attributes:
            match = re.search(regexp, line)
            if match:
                value = match.group(1) if (convert_func is None) else convert_func(match)
                if hasattr(self, attr) and getattr(self, attr) != default:
                    setattr(self, attr, getattr(self, attr) + value)
                else:
                    setattr(self, attr, value)
                return True
        return False
