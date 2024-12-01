class BatchSplitter:
    """ Class to split a batch into smaller batches """

    def __init__(self, batch_size):
        self.batch_size = batch_size

    def split(self, data):
        """ Split the data into batches """
        for i in range(0, len(data), self.batch_size):
            yield data[i: i + self.batch_size]
