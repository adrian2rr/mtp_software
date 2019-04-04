import zlib


class Compression(object):

	def create_fragments(self, document_string, payload_size, blocks):
		self.doc = document_string
		self.payload_size = payload_size
		self.blocks = blocks
		self.total_file_size = len(self.doc)
		self.N = int(self.total_file_size/self.payload_size)
		self.compressed_list = []
		self.decompressed_list = []
		# if read file is not a multiple of 32 cut it
		# TODO add padding
		if(self.total_file_size%self.N != 0):
		    self.doc = self.doc[:self.N]
		    self.new_file_size = self.N*self.payload_size
		else:
		    self.new_file_size = self.total_file_size

		self.block_size = int((self.N*self.payload_size)/self.blocks)
		self.fragments = [self.doc[i:i+self.block_size] for i in range(0, self.new_file_size, self.block_size)]


	def encode(self, compression_level):
		for string in self.fragments:
			self.compressed_list.append(zlib.compress(string, compression_level))
		return self.compressed_list
	
	def decode(self,  compressed_list):
            for string in compressed_list:
                self.decompressed_list.append(zlib.decompress(string))
            return self.decompressed_list

