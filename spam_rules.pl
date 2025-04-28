% =============================
% Spam Detection Rules - Prolog
% =============================

% --- Include blacklist facts ---
:- consult('blacklist.pl').

% Load the spam keywords from the separate file
:- [keywords].  % This loads the facts from keywords.pl

% --- Rule: Check if message contains a spam keyword ---
contains_spam_keyword(Msg) :-
    spam_keyword(Word),
    sub_string(Msg, _, _, _, Word).

% --- Rule: Check if message contains a URL/link ---
contains_link(Msg) :-
    sub_string(Msg, _, _, _, "http://");
    sub_string(Msg, _, _, _, "https://");
    sub_string(Msg, _, _, _, "www.").

% --- Rule: Message is all uppercase and long enough ---
all_caps(Msg) :-
    string_upper(Msg, Msg),
    string_length(Msg, Len),
    Len > 5.

% --- Rule: Message has excessive punctuation ---
excessive_punctuation(Msg) :-
    sub_string(Msg, _, _, _, "!!!");
    sub_string(Msg, _, _, _, "???").

% --- Rule: Message contains a currency symbol ---
contains_currency_symbol(Msg) :-
    sub_string(Msg, _, _, _, '$');
    sub_string(Msg, _, _, _, "₹");
    sub_string(Msg, _, _, _, "€").

% --- Rule: Message contains a phone number pattern ---
contains_phone_number(Msg) :-
    re_matchsub("\\+?[0-9]{10,}", Msg, _, []).

% --- Helper to count how many rules apply ---
spam_score(Msg, Score) :-
    findall(1, (
        (
            contains_spam_keyword(Msg);
            contains_link(Msg);
            all_caps(Msg);
            excessive_punctuation(Msg);
            contains_currency_symbol(Msg);
            contains_phone_number(Msg)
        )
    ), Matches),
    length(Matches, Score).

% --- Main Spam Checking Rule ---
is_spam(Email) :-
    % If sender is blacklisted, immediate spam
    blacklisted_sender(Email.sender), !.

is_spam(Email) :-
    % Else use normal content-based rules
    spam_score(Email.body, Score),
    Score >= 2.
