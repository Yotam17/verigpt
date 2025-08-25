/* Copyright 2018 Tymoteusz Blazejczyk
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

`include "logic.svh"

/* Module: logic_reset_synchronizer
 *
 * Synchronize asynchronous reset de-assertion to clock.
 *
 * Parameters:
 *  STAGES          - Number of registers used for reset synchronization.
 *  RESETS          - Number of input resets.
 *
 * Ports:
 *  aclk            - Clock.
 *  areset_n        - Asynchronous active-low reset.
 *  areset_n_synced - Asynchronous reset assertion.
 *                    Synchronous reset de-assertion.
 */
module logic_reset_synchronizer #(
    int STAGES = 2,
    int RESETS = 1
) (
    input aclk,
    input [RESETS-1:0] areset_n,
    output logic areset_n_synced
);
    initial begin: design_rule_checks
        `LOGIC_DRC_EQUAL_OR_GREATER_THAN(STAGES, 2)
    end

    genvar k;

    logic [RESETS-1:0] areset_n_q;

    generate
        for (k = 0; k < RESETS; ++k) begin: resets
            logic_reset_synchronizer_unit #(
                .STAGES(STAGES)
            )
            unit (
                .areset_n(areset_n[k]),
                .areset_n_synced(areset_n_q[k]),
                .*
            );
        end

        if (RESETS > 1) begin: enabled_multi_resets
            logic_reset_synchronizer_unit #(
                .STAGES(STAGES)
            )
            unit (
                .areset_n(&areset_n_q),
                .*
            );
        end
        else begin: enabled_one_reset
            always_comb areset_n_synced = areset_n_q[0];
        end
    endgenerate
endmodule
