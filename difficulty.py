class Difficulty:        
     # this allows you to control the speed at which new blocks can be added

    @classmethod
    def bits_to_target(cls, bits):
        """converts a decimal number(bits) and converts it
        to the 64 bit hexidecimal target which dictates difficulty
        """ 
        bits= int(bits , 16)
        shift = bits >> 24 
        value = bits & 0x00ffffff
        value <<= 8 * (shift - 3)            
        target = hex(value)
        target = cls.pad_lead_zeros(target)
        return target    

    @staticmethod
    def target_to_bits(target):
        """converts a 64 bit hexadecimal and converts it
        to a decimal (bits) which dictates difficulty
        """
        bitlength = target.bit_length() + 1 
        size = int( (bitlength + 7) / 8 )
        value = target >> 8 * (size - 3)
        value |= size << 24 
        return value

    @staticmethod
    def pad_lead_zeros(hex_str):
        hex_num = hex_str[2:]
        num_zeros_needed = 64 - len(hex_num)
        padded_hex_str = '0x%s%s' % ('0' * num_zeros_needed, hex_num)
        return padded_hex_str

    @classmethod
    def bits_to_difficulty( cls, bits, genesis_bits):
        
        """Finds the difficulty in proportion to the effort to mine the first blocks"""
        genesis_target =  cls.bits_to_target(gensis_bits)
        target = cls.bits_to_target(bits)
        difficulty =  genesis_target / float(target)
        return difficulty

    @classmethod
    def update_difficulty(cls, Blockchain, block, blocks_to_update, time_per_block):
        """Updates the difficulty every x blocks by averaging
            past block mining time and comparing to desired time
            desired_time: Desired average time in seconds to mine a block
            blocks_to_update: update difficulty after every x blocks 
            """

        bits = block.bits
        target = int(cls.bits_to_target(bits), 16)
        #print('Index    :', (block.index + 1))

        if block.index  == (blocks_to_update - 1 ):
            first_block_secs = Blockchain[-1 * blocks_to_update ].timestamp
            last_block_secs = block.timestamp 
            time_span_secs = last_block_secs - first_block_secs 
            avg_time_block= time_span_secs / (blocks_to_update - 1)
            print('AVG time of last {} blocks: {} sec'.format((blocks_to_update-1), round(avg_time_block,2))) 
            new_target =  target * (avg_time_block / time_per_block)
            bits = hex(cls.target_to_bits(int(new_target)))
            print('New Bits :', bits)
            
        elif ((block.index + 1) %  blocks_to_update) == 0:
            first_block_secs = Blockchain[-1 * (blocks_to_update + 1)].timestamp
            last_block_secs = block.timestamp 
            time_span_secs = last_block_secs - first_block_secs
            avg_time_block= time_span_secs / blocks_to_update
            print('AVG time of last {} blocks: {} sec'.format(blocks_to_update,round(avg_time_block,2)))
            new_target  = target * (avg_time_block / time_per_block)
            bits = hex(cls.target_to_bits(int(new_target)))
            print('New Bits :', bits)
        return bits
    