import backtrader as bt

class MeanReversionStrategy(bt.Strategy):
    params = (
        ('ema_len', 200),
        ('rsi_len', 14),
        ('tp_sl_mul', False),
        ('risk', 1),
        ('atr_bars', 14),
        ('stop_mult', 3),
        ('tp_mult', 5),
        ('tp1_mult', 0.75),
        ('tp2_mult', 1.5),
        ('tp_close', 15)
    )

    def __init__(self):
        self.ema = bt.indicators.ExponentialMovingAverage(self.data, period=self.params.ema_len)
        self.rsi = bt.indicators.RSI(self.data, period=self.params.rsi_len)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_bars)

        self.long_stop_level = self.data.close
        self.long_profit_level = self.data.close
        self.short_stop_level = self.data.close
        self.short_profit_level = self.data.close

    def next(self):
        go_long = self.data.open <= self.data.close[-1] and self.data.close > self.data.open[-1] and self.data.open[-1] > self.data.close[-1]
        go_short = self.data.open >= self.data.close[-1] and self.data.close < self.data.open[-1] and self.data.open[-1] < self.data.close[-1]

        # ------ GET IN/OUT A TRADE ------
        in_long_position = self.position.size > 0
        in_short_position = self.position.size < 0
        not_in_trade = self.position.size == 0

        # For long
        self.long_stop_level = bt.If(
            go_long and self.not_in_trade,
            self.data.close - self.atr * self.params.stop_mult,
            bt.If(self.long_stop_level(-1), self.long_stop_level(-1), self.long_stop_level)
            # Use previous value if available
        )
        self.long_profit_level = bt.If(
            go_long and not_in_trade,
            self.data.close + self.atr * self.params.tp_mult,
            bt.If(self.long_profit_level(-1), self.long_profit_level(-1), self.long_profit_level)
        )

        # For short
        short_stop_level = bt.If(
             go_short and not_in_trade,
             self.data.close + self.atr * self.params.stop_mult,
             bt.If(self.short_stop_level(-1), self.short_stop_level(-1), self.short_stop_level)
             )
        short_profit_level = bt.If(
            go_short and not_in_trade,
            self.data.close - self.atr * self.params.tp_mult,
            bt.If(self.short_profit_level(-1), self.short_profit_level(-1), self.short_profit_level)
        )

        # Execute buy or sell order
        if go_long and not_in_trade:
            denominator = abs(self.data.close - self.long_stop_level)

            # Check if denominator is non-zero before performing division
            if denominator != 0:
                size = (self.broker.get_cash() * self.params.risk) / denominator
                self.buy(size=size)
        elif go_short and not_in_trade:
            denominator = abs(self.data.close - self.short_stop_level)

            # Check if denominator is non-zero before performing division
            if denominator != 0:
                size = (self.broker.get_cash() * self.params.risk) / denominator
                self.sell(size=size)

        # Exit or breakeven
        long_break_stop = self.position.price + 2 * (self.position.price * 0.001)
        short_break_stop = self.position.price - 2 * (self.position.price * 0.001)

        if in_long_position:
            if self.data.close > self.ema:
                self.close()
            breakeven_level = self.position.price + self.params.tp1_mult * (self.position.price - self.long_stop_level)
            if self.data.high > breakeven_level:
                self.close()
            elif in_short_position:
                if self.data.close < self.ema:
                    self.close()
                breakeven_level = self.position.price - self.params.tp1_mult * (short_stop_level - self.position.price)
                if self.data.low < breakeven_level:
                    self.close()

            self.plot("Long Breakeven", long_break_stop)
            self.plot("Short Breakeven", short_break_stop)

