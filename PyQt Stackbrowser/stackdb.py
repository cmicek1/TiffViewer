import pandas as pd


class StackDb:
    """
    Pandas DataFrame for MapManager spine points and associated metadata.
    """
    def __init__(self, fname):
        """
        Constructor; allows user interaction with database.

        :param fname: Path to the file containing stackdb info. Expected name format is XXXX_sY_db2.txt,
                      where XXXX is the session name and Y is the session number

        :type fname: str
        """
        self.data = {}
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

        self.dframe = pd.read_csv(fname, skiprows=1)

        if 'voxelx' in self.data:
            self.dx = self.data['voxelx']
        if 'voxely' in self.data:
            self.dy = self.data['voxely']
        if 'voxelz' in self.data:
            self.dz = self.data['voxelz']