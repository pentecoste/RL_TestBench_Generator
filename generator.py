import random

num_files = input("Quanti casi di test vuoi generare?\n")

def populate_values(vals, n):
    for i in range(n):
        rand = random.randint(0, 1200)
        vals.append(0 if rand > 255 else rand)
        vals.append(0)

def elaborate(vals, out_vals, n):
    prec_val = 0
    cred = 0
    i = 0
    while i < 2*k:
        if vals[i] != 0:
            prec_val = vals[i]
            cred = 31
        else:
            if cred > 0:
                cred = cred - 1
        out_vals.append(prec_val)
        out_vals.append(cred)
        i = i + 2

data_struct = []
for i in range(int(num_files)):
    temp_arr = []
    in_values = []
    out_values = []
    k = random.randint(1, 400)
    populate_values(in_values, k)
    elaborate(in_values, out_values, k)
    rand_address = random.randint(0, 65565 - 2*k)
    in_values_str = ""
    for v in in_values:
        in_values_str += str(v) + ", "
    in_values_str = in_values_str[:-2]
    out_values_str = ""
    for v in out_values:
        out_values_str += str(v) + ", "
    out_values_str = out_values_str[:-2]
    temp_arr.append(in_values_str)
    temp_arr.append(out_values_str)
    temp_arr.append(rand_address)
    temp_arr.append(k)
    data_struct.append(temp_arr)

with open("output.vhd", "w") as f_out:
    f_out.write('''library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;

entity project_tb is
end project_tb;

architecture project_tb_arch of project_tb is
    constant CLOCK_PERIOD : time := 20 ns;
    signal tb_clk : std_logic := '0';
    signal tb_rst, tb_start, tb_done : std_logic;
    signal tb_add : std_logic_vector(15 downto 0);
    signal tb_k   : std_logic_vector(9 downto 0);

    signal tb_o_mem_addr, exc_o_mem_addr, init_o_mem_addr : std_logic_vector(15 downto 0);
    signal tb_o_mem_data, exc_o_mem_data, init_o_mem_data : std_logic_vector(7 downto 0);
    signal tb_i_mem_data : std_logic_vector(7 downto 0);
    signal tb_o_mem_we, tb_o_mem_en, exc_o_mem_we, exc_o_mem_en, init_o_mem_we, init_o_mem_en : std_logic;

    type ram_type is array (65535 downto 0) of std_logic_vector(7 downto 0);
    signal RAM : ram_type := (OTHERS => "00000000");

    ''')
    for i in range(int(num_files)):
        f_out.write('''constant SCENARIO_LENGTH''' + str(i) + ''' : integer := ''' + str(data_struct[i][3]) + ''';
    constant SCENARIO_ADDRESS''' + str(i) + ''' : integer := ''' + str(data_struct[i][2]) + ''';
    type scenario_type''' + str(i) + ''' is array (0 to SCENARIO_LENGTH''' + str(i) + '''*2-1) of integer;

    signal scenario_input''' + str(i) + ''' : scenario_type''' + str(i) + ''' := (''' + data_struct[i][0] + ''');
    signal scenario_full''' + str(i) + '''  : scenario_type''' + str(i) + ''' := (''' + data_struct[i][1] + ''');
    
    ''')

    f_out.write('''
    signal memory_control : std_logic := '0';

    component project_reti_logiche is
        port (
                i_clk : in std_logic;
                i_rst : in std_logic;
                i_start : in std_logic;
                i_add : in std_logic_vector(15 downto 0);
                i_k   : in std_logic_vector(9 downto 0);
                
                o_done : out std_logic;
                
                o_mem_addr : out std_logic_vector(15 downto 0);
                i_mem_data : in  std_logic_vector(7 downto 0);
                o_mem_data : out std_logic_vector(7 downto 0);
                o_mem_we   : out std_logic;
                o_mem_en   : out std_logic
        );
    end component project_reti_logiche;

begin
    UUT : project_reti_logiche
    port map(
                i_clk   => tb_clk,
                i_rst   => tb_rst,
                i_start => tb_start,
                i_add   => tb_add,
                i_k     => tb_k,
                
                o_done => tb_done,
                
                o_mem_addr => exc_o_mem_addr,
                i_mem_data => tb_i_mem_data,
                o_mem_data => exc_o_mem_data,
                o_mem_we   => exc_o_mem_we,
                o_mem_en   => exc_o_mem_en
    );

    -- Clock generation
    tb_clk <= not tb_clk after CLOCK_PERIOD/2;

    -- Process related to the memory
    MEM : process (tb_clk)
    begin
        if tb_clk'event and tb_clk = '1' then
            if tb_o_mem_en = '1' then
                if tb_o_mem_we = '1' then
                    RAM(to_integer(unsigned(tb_o_mem_addr))) <= tb_o_mem_data after 1 ns;
                    tb_i_mem_data <= tb_o_mem_data after 1 ns;
                else
                    tb_i_mem_data <= RAM(to_integer(unsigned(tb_o_mem_addr))) after 1 ns;
                end if;
            end if;
        end if;
    end process;
    
    memory_signal_swapper : process(memory_control, init_o_mem_addr, init_o_mem_data,
                                    init_o_mem_en,  init_o_mem_we,   exc_o_mem_addr,
                                    exc_o_mem_data, exc_o_mem_en, exc_o_mem_we)
    begin
        -- This is necessary for the testbench to work: we swap the memory
        -- signals from the component to the testbench when needed.
    
        tb_o_mem_addr <= init_o_mem_addr;
        tb_o_mem_data <= init_o_mem_data;
        tb_o_mem_en   <= init_o_mem_en;
        tb_o_mem_we   <= init_o_mem_we;

        if memory_control = '1' then
            tb_o_mem_addr <= exc_o_mem_addr;
            tb_o_mem_data <= exc_o_mem_data;
            tb_o_mem_en   <= exc_o_mem_en;
            tb_o_mem_we   <= exc_o_mem_we;
        end if;
    end process;
    
    -- This process provides the correct scenario on the signal controlled by the TB
    create_scenario : process
    begin
        wait for 50 ns;

        -- Signal initialization and reset of the component
        tb_start <= '0';
        tb_add <= (others=>'0');
        tb_k   <= (others=>'0');
        tb_rst <= '1';
        
        -- Wait some time for the component to reset...
        wait for 50 ns;
        
        tb_rst <= '0';
        
        ''')
    for i in range(int(num_files)):
        f_out.write('''memory_control <= '0';  -- Memory controlled by the testbench
        ''')
        if (random.randint(1, 50) <= 5):
            f_out.write('''tb_rst <= '1';

            wait for 50 ns;

            tb_rst <= '0';

            ''')

        f_out.write('''wait until falling_edge(tb_clk); -- Skew the testbench transitions with respect to the clock

        -- Configure the memory        
        for i in 0 to SCENARIO_LENGTH''' + str(i) + '''*2-1 loop
            init_o_mem_addr<= std_logic_vector(to_unsigned(SCENARIO_ADDRESS''' + str(i) + '''+i, 16));
            init_o_mem_data<= std_logic_vector(to_unsigned(scenario_input''' + str(i) + '''(i),8));
            init_o_mem_en  <= '1';
            init_o_mem_we  <= '1';
            wait until rising_edge(tb_clk);   
        end loop;
        
        wait until falling_edge(tb_clk);

        memory_control <= '1';  -- Memory controlled by the component
        
        tb_add <= std_logic_vector(to_unsigned(SCENARIO_ADDRESS''' + str(i) + ''', 16));
        tb_k   <= std_logic_vector(to_unsigned(SCENARIO_LENGTH''' + str(i) + ''', 10));
        
        tb_start <= '1';

        while tb_done /= '1' loop                
            wait until rising_edge(tb_clk);
        end loop;

        wait for 5 ns;
        
        tb_start <= '0';

        wait for 50 ns;
        
        ''')

    f_out.write('''wait;
        
    end process;

    -- Process without sensitivity list designed to test the actual component.
    test_routine : process
    begin

        wait until tb_rst = '1';
        wait for 25 ns;
        assert tb_done = '0' report "TEST FALLITO o_done !=0 during reset" severity failure;
        wait until tb_rst = '0';

        wait until falling_edge(tb_clk);
        assert tb_done = '0' report "TEST FALLITO o_done !=0 after reset before start" severity failure;
        
        ''')

    for i in range(int(num_files)):
        f_out.write('''wait until rising_edge(tb_start);

        while tb_done /= '1' loop                
            wait until rising_edge(tb_clk);
        end loop;

        assert tb_o_mem_en = '0' or tb_o_mem_we = '0' report "TEST FALLITO o_mem_en !=0 memory should not be written after done." severity failure;

        for i in 0 to SCENARIO_LENGTH''' + str(i) + '''*2-1 loop
            assert RAM(SCENARIO_ADDRESS''' + str(i) + '''+i) = std_logic_vector(to_unsigned(scenario_full''' + str(i) + '''(i),8)) report "TEST FALLITO @ OFFSET=" & integer'image(i) & " expected= " & integer'image(scenario_full''' + str(i) + '''(i)) & " actual=" & integer'image(to_integer(unsigned(RAM(i)))) severity failure;
        end loop;

        wait until falling_edge(tb_done);
        
        ''')

    f_out.write('''assert false report "Simulation Ended! TEST PASSATO" severity failure;
    end process;

end architecture;''')

