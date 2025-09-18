class Chunker:
    """
    A class to handle the chunking of text documents into smaller segments.

    Attributes:
        chunk_size (int): The maximum size of each chunk.
    """

    def __init__(self, chunk_size=512):
        """
        Initializes the Chunker with a specified chunk size.

        Args:
            chunk_size (int): The maximum size of each chunk. Default is 512.
        """
        self.chunk_size = chunk_size
        self.chunks = []

    def chunk_text(self, text):
        """
        Splits the input text into smaller chunks based on the specified chunk size.

        Args:
            text (str): The text to be chunked.

        Returns:
            list: A list of text chunks.
        """
        self.chunks = [text[i:i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]
        return self.chunks

    def get_chunks(self):
        """
        Returns the list of chunks created from the last chunking operation.

        Returns:
            list: A list of text chunks.
        """
        return self.chunks

    # TODO: Consider adding functionality for overlapping chunks or different chunking strategies in the future.