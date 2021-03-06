"""
Copyright (c) 2009 Ryan Kirkman

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

import math

class Player:
    # Class attribute
    # The system constant, which constrains
    # the change in volatility over time.

    def __init__(self, name, rating=1500, rd=350, vol=0.08):
        # For testing purposes, preload the values
        # assigned to an unrated player.
        self.rating = rating
        self.name = name
        self.rd = rd
        self.vol = vol
        self.opponentList = []
        self.resultList = []
        self.inactivity = 0
        self.updated = 0

    _tau = 1.0

    @property
    def rating(self):
        return (self.__rating * 173.7178) + 1500

    @rating.setter
    def rating(self, rating):
        self.__rating = (rating - 1500) / 173.7178

    @property
    def rd(self):
        return self.__rd * 173.7178

    @rd.setter
    def rd(self, rd):
        self.__rd = rd / 173.7178

    @property
    def opponentList(self):
        return self.__opponentList

    @opponentList.setter
    def opponentList(self, opponentList):
        self.__opponentList = opponentList

    @property
    def resultList(self):
        return self.__resultList

    @resultList.setter
    def resultList(self, resultList):
        self.__resultList = resultList

    def addMatch(self, opponent, result):
        # opponent is a Player object, result is 1 for win and 0 for loss
        self.opponentList.append(opponent)
        self.resultList.append(result)

    def clearMatches(self):
        self.opponentList = []
        self.resultList = []

    def _preRatingRD(self):
        """ Calculates and updates the player's rating deviation for the
        beginning of a rating period.

        preRatingRD() -> None

        """
        self.__rd = math.sqrt(math.pow(self.__rd, 2) + math.pow(self.vol, 2))

    def updatePlayer(self, mode):
        """ Calculates the new rating and rating deviation of the player.

        update_player(list[int], list[int], list[bool]) -> None

        """
        self.updated = 1
        if len(self.opponentList) == 0:
            if mode == 0:
                self.didNotCompete()
            return

        self.inactivity = 0

        rating_list = [(x.rating - 1500) / 173.7178 for x in self.opponentList]
        RD_list = [x.rd / 173.7178 for x in self.opponentList]

        v = self._v(rating_list, RD_list)
        self.vol = self._newVol(rating_list, RD_list, v)
        self._preRatingRD()

        self.__rd = 1 / math.sqrt((1 / math.pow(self.__rd, 2)) + (1 / v))

        tempSum = 0
        for i in range(len(rating_list)):
            tempSum += self._g(RD_list[i]) * \
                       (self.resultList[i] - self._E(rating_list[i], RD_list[i]))
        self.__rating += math.pow(self.__rd, 2) * tempSum
        self.clearMatches()

    def _newVol(self, rating_list, RD_list, v):
        """ Calculating the new volatility as per the Glicko2 system.

        _newVol(list, list, list) -> float

        """
        i = 0
        delta = self._delta(rating_list, RD_list, v)
        a = math.log(math.pow(self.vol, 2))
        tau = self._tau
        x0 = a
        x1 = 0

        while x0 != x1:
            # New iteration, so x(i) becomes x(i-1)
            x0 = x1
            d = math.pow(self.__rating, 2) + v + math.exp(x0)
            h1 = -(x0 - a) / math.pow(tau, 2) - 0.5 * math.exp(x0) \
                                                / d + 0.5 * math.exp(x0) * math.pow(delta / d, 2)
            h2 = -1 / math.pow(tau, 2) - 0.5 * math.exp(x0) * \
                                         (math.pow(self.__rating, 2) + v) \
                                         / math.pow(d, 2) + 0.5 * math.pow(delta, 2) * math.exp(x0) \
                                                            * (
                                                            math.pow(self.__rating, 2) + v - math.exp(x0)) / math.pow(d,
                                                                                                                      3)
            x1 = x0 - (h1 / h2)

        return math.exp(x1 / 2)

    def _delta(self, rating_list, RD_list, v):
        """ The delta function of the Glicko2 system.

        _delta(list, list, list) -> float

        """
        tempSum = 0
        for i in range(len(rating_list)):
            tempSum += self._g(RD_list[i]) * (self.resultList[i] - self._E(rating_list[i], RD_list[i]))
        return v * tempSum

    def _v(self, rating_list, RD_list):
        """ The v function of the Glicko2 system.

        _v(list[int], list[int]) -> float

        """
        tempSum = 0
        for i in range(len(rating_list)):
            tempE = self._E(rating_list[i], RD_list[i])
            tempSum += math.pow(self._g(RD_list[i]), 2) * tempE * (1 - tempE)
        return 1 / tempSum

    def _E(self, p2rating, p2RD):
        """ The Glicko E function.

        _E(int) -> float

        """
        return 1 / (1 + math.exp(-1 * self._g(p2RD) * \
                                 (self.__rating - p2rating)))

    def _g(self, RD):
        """ The Glicko2 g(RD) function.

        _g() -> float

        """
        return 1 / math.sqrt(1 + 3 * math.pow(RD, 2) / math.pow(math.pi, 2))

    def didNotCompete(self):
        """ Applies Step 6 of the algorithm. Use this for
        players who did not compete in the rating period.

        did_not_compete() -> None

        """
        self._preRatingRD()
        self.inactivity += 1
        if self.inactivity > 1:
            self.rd += 3
        if self.inactivity > 3:
            self.rd += 4
        if self.inactivity > 5:
            self.rd += 5

    def getAttributes(self):
        rating = self.rating
        name = self.name
        rd = self.rd
        vol = self.vol
        inactivity = self.inactivity
        # opponentList = self.opponentList
        # resultList = self.resultList

        return name, rating, rd, vol, inactivity


class Match:

    def __init__(self, winner, loser, wScore, lScore, date):
        self.winner = winner
        self.loser = loser
        self.wScore = wScore
        self.lScore = lScore
        self.date = date

    def addMatchToPlayers(self):
        self.winner.addMatch(self.loser, 1)
        self.loser.addMatch(self.winner, 0)
