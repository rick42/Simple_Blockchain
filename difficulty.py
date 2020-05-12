class Difficulty:        
     # this allows you to control the speed at which new blocks can be added

    def bits_to_target(bits):
        """converts a decimal number bit and converts it
        to the 32 byte hex target which dictates difficulty""" 
        bits= int(bits , 16)
        shift = bits >> 24 
        value = bits & 0x00ffffff
        value <<= 8 * (shift - 3)            
        target = hex(value)
        target = Difficulty.pad_lead_zeros(target)
        return target    

    def target_to_bits(target):
        bitlength = target.bit_length() + 1 
        size = int( (bitlength + 7) / 8 )
        value = target >> 8 * (size - 3)
        value |= size << 24 
        return value

    def pad_lead_zeros(hex_str):
        hex_num = hex_str[2:]
        num_zeros_needed = 64 - len(hex_num)
        padded_hex_str = '0x%s%s' % ('0' * num_zeros_needed, hex_num)
        return padded_hex_str

    def bits_to_difficulty(bits, genesis_bits):
        """Finds the difficulty in proportion to the effort to mine the first blocks"""
        genesis_target =  bits_to_target(gensis_bits)
        target = bits_to_target(bits)
        difficulty =  genesis_target / float(target)
        return difficulty

    def update_difficulty(Blockchain, block, blocks_to_update = 5, desired_time_block = 10.0 ):
        """Updates the difficulty every x blocks by averaging
            past block mining time and comparing to desired time
            desired_time: Desired time in seconds to mine a block
            blocks_to_update: update difficulty after every x blocks 
            """

        bits = block.bits
        target = int(Difficulty.bits_to_target(bits), 16)
        
        if block.index  == (blocks_to_update - 1 ):
            first_block_secs = Blockchain[-1 * blocks_to_update ].timestamp
            last_block_secs = block.timestamp 
            time_span_secs = last_block_secs - first_block_secs 
            avg_time_block= time_span_secs / (blocks_to_update - 1)
            new_target =  target * (avg_time_block / desired_time_block)
            bits = hex(Difficulty.target_to_bits(int(new_target)))
            
        elif ((block.index + 1) %  blocks_to_update) == 0:
            first_block_secs = Blockchain[-1 * (blocks_to_update + 1)].timestamp
            last_block_secs = block.timestamp 
            time_span_secs = last_block_secs - first_block_secs
            avg_time_block= time_span_secs / blocks_to_update
            print('AVG time of last {} blocks: {} sec'.format(blocks_to_update,avg_time_block))
            new_target  = target * (avg_time_block / desired_time_block)
            bits = hex(Difficulty.target_to_bits(int(new_target)))

        return bits
    