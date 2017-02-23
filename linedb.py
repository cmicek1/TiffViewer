import pandas as pd


class LineDb:
    """
    Pandas DataFrame for MapManager lines.
    """
    def __init__(self, fname):
        """
        Constructor; allows user interaction with database.

        :param fname: Path to the file containing line info. Expected name format is XXXX_sY_l.txt,
                      where XXXX is the session name and Y is the session number

        :type fname: str
        """
        self.data = {}
        skip = 7
        with open(fname, 'rU') as f:
            line = f.readline().split(';')
            if len(line) > 0:
                line = line[:-1]
            for pair in line:
                _ = pair.split('=')
                val = _[1]
                if val.isdigit():
                    val = int(val)
                elif val == 'None':
                    val = None
                else:
                    try:
                        val = float(val)
                    except ValueError:
                        pass
                self.data.update({_[0]: val})

        if 'numHeaderRow' in self.data:
            skip = self.data['numHeaderRow'] + 2
        self.dframe = pd.read_csv(fname, skiprows=skip)
