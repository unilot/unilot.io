pragma solidity ^0.4.16;

interface Game {
    event GameStarted(uint betAmount);
    event NewPlayerAdded(uint balance);
    event GameFinished(address winner);

    function () public payable;                          //Participate in game. Proxy for play method
    function play() public payable;                      //Participate in game.
    function getPrizeAmount() public constant returns (uint);     //Get potential or actual prize amount
    function getNumWinners() public constant returns(uint, uint);
    function getPlayers() public constant returns(address[]);     //Get full list of players
    function getWinners() public constant returns(address[]);     //Get winners. Accessable only when finished
    function getStat() public constant returns(uint, uint, uint);       //Short stat on game

    function calcaultePrizes() public constant returns (uint[]);

    function finish() public;                        //Closes game chooses winner

    // function revoke();                     //Stop game and return money to players
    // function move(address nextGame);       //Move players bets to another game
}

library TicketLib {
    struct Ticket {
        address player;
        address currentGame;
        bool is_winner;
        bool is_active;
        uint block_number;
        uint block_time;
        uint num_votes;
    }
}

contract BaseUnilotGame is Game {
    enum State {
        ACTIVE,
        ENDED,
        REVOKED,
        MOVED
    }

    State state;
    address administrator;
    uint bet;

    //Calculation constants
    uint  constant accuracy                   = 1000000000000000000;
    uint  constant MAX_X_FOR_Y                = 195;  // 19.5

    uint  constant minPrizeCoeficent          = 1;
    uint  constant percentOfWinners           = 5;    // 5%
    uint  constant percentOfFixedPrizeWinners = 20;   // 20%
    uint  constant gameCommision              = 20;   // 20%
    uint  constant bonusGameCommision         = 5;    // 5%
    uint  constant tokenHolerGameCommision    = 5;    // 5%
    // End Calculation constants

    mapping (address => TicketLib.Ticket) internal tickets;
    address[] internal ticketIndex;

    //Modifiers
    modifier onlyAdministrator() {
        require(msg.sender == administrator);
        _;
    }

    modifier onlyPlayer() {
        require(msg.sender != administrator);
        _;
    }

    modifier validBet() {
        require(msg.value == bet);
        _;
    }

    modifier activeGame() {
        require(state == State.ACTIVE);
        _;
    }

    //Private methods


    function ()
        public
        payable
        validBet
        onlyPlayer
    {
        play();
    }

    function play() public payable;

    function getPrizeAmount()
        public
        constant
        returns (uint result)
    {
        uint totalCommision = gameCommision
                            + bonusGameCommision
                            + tokenHolerGameCommision;

        //Calculation is odd on purpose.  It is a sort of ceiling effect to
        // maximize amount of prize
        result = ( this.balance - ( ( this.balance * totalCommision) / 100) );

        return result;
    }

    function getNumWinners()
        public
        constant
        returns (uint numWinners, uint numFixedAmountWinners)
    {
        // Calculation is odd on purpose. It is a sort of ceiling effect to
        // maximize number of winners
        uint totaNumlWinners = ( ticketIndex.length - ( (ticketIndex.length * ( 100 - percentOfWinners ) ) / 100 ) );


        numFixedAmountWinners = (totaNumlWinners * percentOfFixedPrizeWinners) / 100;
        numWinners = totaNumlWinners - numFixedAmountWinners;

        return (numWinners, numFixedAmountWinners);
    }

    function getPlayers()
        public
        constant
        returns(address[])
    {
        return ticketIndex;
    }

    function getWinners()
        public
        constant
        returns(address[] memory result)
    {
        var(numWinners, numFixedAmountWinners) = getNumWinners();
        uint totalNumWinners = numWinners + numFixedAmountWinners;
        result = new address[](totalNumWinners);


        for (uint i = 0; i < ticketIndex.length; i++) {
            if (tickets[ticketIndex[i]].is_winner == true) {
                result[i] = ticketIndex[i];
            }
        }

        return result;
    }

    function getStat()
        public
        constant
        returns ( uint, uint, uint )
    {
        var (numWinners, numFixedAmountWinners) = getNumWinners();
        return (ticketIndex.length, getPrizeAmount(), uint(numWinners + numFixedAmountWinners));
    }

    function calcaultePrizes()
        public
        constant
        returns(uint[] prizes)
    {
        var (numWinners, numFixedAmountWinners) = getNumWinners();
        uint totalNumWinners = ( numWinners + numFixedAmountWinners );

        prizes = new uint[](totalNumWinners);
        uint[] memory y = new uint[]((numWinners - 1));
        uint z = 0; // Sum of all Y values
        uint step = ( MAX_X_FOR_Y * accuracy / 10 ) / numWinners;

        if ( totalNumWinners == 1 ) {
            prizes[0] = getPrizeAmount();

            return prizes;
        } else if ( totalNumWinners < 1 ) {
            return prizes;
        }

        for (uint i = 0; i < y.length; i++) {
            uint x = step * (i);

            y[i] = ((1*accuracy**2) / (x + (5*accuracy/10))) - ((5 * accuracy) / 100);
            z += y[i];
        }

        prizes = distributePrizeCalculation(z, y, numWinners, numFixedAmountWinners);

        return prizes;
    }

    function distributePrizeCalculation (uint z, uint[] y, uint numWinners, uint numFixedAmountWinners)
        private
        constant
        returns (uint[] prizes)
    {
        uint totalNumberOfWinners = numWinners + numFixedAmountWinners;

        uint totalPrizeAmount = getPrizeAmount();
        uint minPrizeAmount = bet * minPrizeCoeficent;

        uint prizeAmountForDeligation = totalPrizeAmount - ( minPrizeAmount * totalNumberOfWinners );

        prizes = new uint[](totalNumberOfWinners);

        uint mainWinnerBaseAmount = ( (prizeAmountForDeligation * accuracy) / ( ( ( z * accuracy ) / ( 2 * y[0] ) ) + ( 1 * accuracy ) ) );
        uint undeligatedAmount = prizeAmountForDeligation - mainWinnerBaseAmount;

        prizes[0] = minPrizeAmount + mainWinnerBaseAmount;

        for ( uint i = 1; i < prizes.length; i++ ) {
            prizes[ i ] = minPrizeAmount;

            if ( i == ( numWinners - 1 ) ) {
                prizes[ i ] += undeligatedAmount;
                undeligatedAmount = 0;
            } else if ( i < numWinners ) {
                uint extraPrize = ( ( y[ i - 1 ] * (prizeAmountForDeligation - mainWinnerBaseAmount) ) / z);
                prizes[ i ] += extraPrize;
                undeligatedAmount -= extraPrize;
            }
        }

        return prizes;
    }
}

contract UnilotTailEther is BaseUnilotGame {

    address winner;
    uint winnerIndex;

    mapping(address => uint) winnersPrizes;
    address[] winnersPrizesIndex;

    //Events
    event Vote(uint index, uint vote, address player);

    //Public methods
    function UnilotEther(uint betAmount)
        public
    {
        state = State.ACTIVE;
        administrator = msg.sender;
        bet = betAmount;

        GameStarted(betAmount);
    }

    function play()
        public
        payable
        validBet
        onlyPlayer
    {
        require(tickets[msg.sender].player == address(0));

        tickets[msg.sender].player       = msg.sender;
        tickets[msg.sender].currentGame  = this;
        tickets[msg.sender].is_winner    = false;
        tickets[msg.sender].is_active    = true;
        tickets[msg.sender].block_number = block.number;
        tickets[msg.sender].block_time   = block.timestamp;
        tickets[msg.sender].num_votes    = 0;

        ticketIndex.push(msg.sender);

        NewPlayerAdded(getPrizeAmount());
    }

    function finish()
        public
        onlyAdministrator
        activeGame
    {

        uint max_votes;

        for (uint i = 0; i < ticketIndex.length; i++) {
            TicketLib.Ticket memory ticket = tickets[ticketIndex[i]];
            uint vote = ( ( ticket.block_number * ticket.block_time ) + uint(ticket.player) ) % ticketIndex.length;

            tickets[ticketIndex[vote]].num_votes += 1;
            uint ticketNumVotes = tickets[ticketIndex[vote]].num_votes;

            if ( ticketNumVotes > max_votes ) {
                max_votes = ticketNumVotes;
                winner = ticketIndex[vote];
                winnerIndex = vote;
            }
        }

        uint[] memory prizes = calcaultePrizes();

        if ( prizes.length == 1 ) {
            winner.transfer(getPrizeAmount());
            tickets[winner].is_winner = true;
        } else {
            address[] memory winners = new address[] (prizes.length);

            uint lastId = winnerIndex;

            for ( i = 0; i < prizes.length; i++ ) {
                if ( i == 0 ) {
                    winners[i] = winner;

                    winnersPrizes[winners[i]] = prizes[i];
                    winnersPrizesIndex.push(winners[i]);

                    winners[i].transfer(prizes[i]);
                    continue;
                }

                if ( lastId == 0 ) {
                    lastId = ticketIndex.length;
                }

                lastId -= 1;
                winners[i] = ticketIndex[lastId];
                winnersPrizes[winners[i]] = prizes[i];
                winnersPrizesIndex.push(winners[i]);
                tickets[winners[i]].is_winner = true;
                winners[i].transfer(prizes[i]);
            }
        }

        state = State.ENDED;
    }
}
