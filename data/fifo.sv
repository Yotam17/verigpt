// Simple FIFO (First-In-First-Out) Buffer Module
// This module implements a basic synchronous FIFO with configurable depth

module fifo #(
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = 4,
    parameter DEPTH = 2**ADDR_WIDTH
)(
    input  logic                   clk,
    input  logic                   rst_n,
    input  logic                   wr_en,
    input  logic                   rd_en,
    input  logic [DATA_WIDTH-1:0] wr_data,
    output logic [DATA_WIDTH-1:0] rd_data,
    output logic                   full,
    output logic                   empty,
    output logic                   overflow,
    output logic                   underflow
);

    // Internal memory array
    logic [DATA_WIDTH-1:0] mem [DEPTH-1:0];
    
    // Read and write pointers
    logic [ADDR_WIDTH-1:0] wr_ptr, rd_ptr;
    
    // Counter for tracking number of elements
    logic [ADDR_WIDTH:0] count;
    
    // Full and empty flags
    assign full = (count == DEPTH);
    assign empty = (count == 0);
    
    // Overflow and underflow detection
    assign overflow = wr_en && full;
    assign underflow = rd_en && empty;
    
    // Write operation
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr <= 0;
            rd_ptr <= 0;
            count <= 0;
        end else begin
            // Write operation
            if (wr_en && !full) begin
                mem[wr_ptr] <= wr_data;
                wr_ptr <= (wr_ptr == DEPTH-1) ? 0 : wr_ptr + 1;
                count <= count + 1;
            end
            
            // Read operation
            if (rd_en && !empty) begin
                rd_data <= mem[rd_ptr];
                rd_ptr <= (rd_ptr == DEPTH-1) ? 0 : rd_ptr + 1;
                count <= count - 1;
            end
        end
    end
    
    // Read data output
    assign rd_data = mem[rd_ptr];

endmodule
