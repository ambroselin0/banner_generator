"""
@Time : 10/13/2020 9:58
@Author : ambrose_lin
@Email : ambroselin001@outlook.com
@File : article_to_banner_text.py
@Project : banner_generator
"""

from tensorflow import keras
from tensorflow.keras.utils import Sequence


class TrainDataFeeder(Sequence):
    def __init__(self):
        pass

    def __len__(self):
        pass

    def __getitem__(self, item):
        pass

    def on_epoch_end(self):
        pass


class Encoder(keras.Model):
    def __init__(self, vocab_size, embedding_dim, hidden_units):
        super(Encoder, self).__init__()
        # Embedding Layer
        self.embedding = keras.layers.Embedding(vocab_size, embedding_dim, mask_zero=True)
        # Encode LSTM Layer
        self.encoder_lstm = keras.layers.LSTM(hidden_units, return_sequences=True, return_state=True,
                                              name="encode_lstm")

    def call(self, inputs):
        encoder_embed = self.embedding(inputs)
        encoder_outputs, state_h, state_c = self.encoder_lstm(encoder_embed)
        return encoder_outputs, state_h, state_c


class Decoder(keras.Model):
    def __init__(self, vocab_size, embedding_dim, hidden_units):
        super(Decoder, self).__init__()
        # Embedding Layer
        self.embedding = keras.layers.Embedding(vocab_size, embedding_dim, mask_zero=True)
        # Decode LSTM Layer
        self.decoder_lstm = keras.layers.LSTM(hidden_units, return_sequences=True, return_state=True,
                                              name="decode_lstm")
        # Attention Layer
        self.attention = keras.layers.Attention()

    def call(self, enc_outputs, dec_inputs, states_inputs):
        decoder_embed = self.embedding(dec_inputs)
        dec_outputs, dec_state_h, dec_state_c = self.decoder_lstm(decoder_embed, initial_state=states_inputs)
        attention_output = self.attention([dec_outputs, enc_outputs])

        return attention_output, dec_state_h, dec_state_c


def Seq2Seq(maxlen, embedding_dim, hidden_units, vocab_size):
    """
    seq2seq model
    """
    # Input Layer
    encoder_inputs = keras.layers.Input(shape=(maxlen,), name="encode_input")
    decoder_inputs = keras.layers.Input(shape=(None,), name="decode_input")
    # Encoder Layer
    encoder = Encoder(vocab_size, embedding_dim, hidden_units)
    enc_outputs, enc_state_h, enc_state_c = encoder(encoder_inputs)
    dec_states_inputs = [enc_state_h, enc_state_c]
    # Decoder Layer
    decoder = Decoder(vocab_size, embedding_dim, hidden_units)
    attention_output, dec_state_h, dec_state_c = decoder(enc_outputs, decoder_inputs, dec_states_inputs)
    # Dense Layer
    dense_outputs = keras.layers.Dense(vocab_size, activation='softmax', name="dense")(attention_output)
    # seq2seq model
    model = keras.models.Model(inputs=[encoder_inputs, decoder_inputs], outputs=dense_outputs)
    return model


if __name__ == '__main__':
    model = Seq2Seq(1000, 100, 100, 100000)
    print(model.summary())
