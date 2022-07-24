* invalid commands have undefined behavior
* errors aren't handled (eg trying to delete a nonexisting file)

echo {word}             print word
echo {word} >{path}     print word to file
ls {path}               list files/dirs
mkdir {path}            mkdir path
rm {path}               remove file or empty dir
cat {path}              cat file

in reality only the first letter is checked:
"mkdir FOO" is equivalent to "monkeyFOO" for example


{0} {255} {128} {1} {10} {32} {36}:
>+>+>+>+[++>[-<++++>]<<]>>
>+>+[+>++[-<+++++++>]<<]>[-<+>]
+>
++++++++++>
>>++++++++[<++++<++++>>-]
<++++


>+sentinel
>invalid command
>rm
>mkdir
>ls
>echo
>cat

+[
    print prompt
    <<<<<<<[<]
    >.>.
    >>.>>.<.

    return to where we were before printing prompt
    [>]>>>>>
    read chars until char 10 (enter) is pressed
    [[<]<<<<<[<]>.>++.--<<.>[>]>>>>>[>],[<]<<<<<[<]>.>.[>]>>>>>[>]<.----------]

    <[<]++++++++[>+++++++++++<-]>
    [->-<]
    >[--[-------[-[-----[<]<]<]<]<]<+
    <-[+<-]

    invalid >[-<<[->+>+<<]>[-<+>>+<]>---.+++++++++++++..[-] +>>>>>>[[-]>] -[+<-]]
    rm      >[- switch to filesystem device & request rm and path <<<<<[<]>.>++++.---->++++.----[>]>>>>>>>>>>[++++++++++.>].
                return cleaning <[[-]<]
                switch back to text device <<<<<<<<[<]>.>.[>]
                return to position >>
                read result and ignore ,[-]
             ]
    mkdir   >[- switch to filesystem device & request mkdir and path <<<<<[<]>.>++++.---->+++.---[>]>>>>>>>>>>>>>[++++++++++.>].
                return cleaning <[[-]<]
                switch back to text device <<<<<<<<[<]>.>.[>]
                return to position >>>
                read result and ignore ,[-]
             ]
    ls      >[- switch to filesystem device & request ls and path <<<<<[<]>.>++++.----<<.>[>]>>>>>>>>>>[++++++++++.>].
               zero path <[[-]<]
               switch back to text device <<<<<<<<[<]>.>.[>]
               sentinel+>>>>
               read zero terminated paths returned ,[
                 [>,]<[<]>
                 read next path
                 >[>]>>>,
               ]
               return to sentinel -[+<-]+>

               stat and print paths
               >>>[
                   <<<
                   switch to filesystem device & request stat
                   generate 255-.
                   generate 132-[-->-<]>+++.>+.->[.>].<[<]
                   switch back to text device -.+<----.[-]<
                   read first byte of stat (isDir) ,[--->]>>>[<]<++++++++++[->+<<+++++++>]
                   print isDir <.[-]>
                   generate and print space ++++[-<++++++++>]<.>
                   read and ignore higher bytes of size ,,,
                   read lowest byte of size and treat it as a single decimal digit ,>[-<+++++>]<--print it.[-]
                   print space <.[-]>>>
                   [.>]> newline++++++++++.[-]>>
               ]
               return to sentinel zeroing cells -[[-]<-]+
               return to initial position
               ->>>>
            ]
    echo    >[>>>[>]>sentinel+++++[-<++++>]<++[<]>>>>[>----------------------]>
              [
                found another space assume it's followed by a lessthan symbol [-]
                >[>]<zero the sentinel[-]
                switch to filesystem device & request write
                generate 255>-.
                generate 132-[-->-<]>+++.<+++.--->[-]
                <<shift filename right <[[->+<]<]
                count and send writeLength<< [[->>+<<]>[-<+>]<+<]...>----.>>
                set a flag indicating we're writing to file <<<<<<+>>>>>>
                advance to filename [>]>
                print filename [++++++++++.>].
                <[[-]<]<[<]<[-]
                >>[>]>
              ]
              <[-]<[<]>>>>>[++++++++++++++++++++++++++++++++.>]<[[-]<]
              return to known position -[+<-]
              <[
                flag indicating we're writing to file is set
                expect to read the return value (and ignore it) ,[-]
              ]>
            ]
    cat     >[- switch to filesystem device & request read and path <<<<<<<[<]>.>++++.---->+.---........++[>]>>>>>>>>>>>[++++++++++.>].
                return cleaning <[[-]<]
                switch back to text device <<<<<<<<[<]>.>.[>]
                return to position >>>>>>
                while result print ,[.,] print newline ++++++++++.[-]
             ]
    >[-]

    reset sentinel <<<<<<<+>>>>>>
    +
]

