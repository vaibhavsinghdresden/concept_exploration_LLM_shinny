from shiny import App, reactive, render, ui, module

@module.ui
def attr_exp_auto_mode_ui():
    return ui.card(ui.div(
                     ui.output_ui("render_starting_ui_auto_mode"),
                     ),
                    ui.div(
                        ui.output_ui("render_steps_and_prompt_input_button"),
                        ui.output_ui("render_start_exploration_button_auto_mode"),
                        ui.output_ui("render_exploration_log_auto_mode"),
                     ),
            )


@module.server
def attr_exp_auto_mode_server(input, output, session, cxt, trigger_recalc):
    models_response_log_auto = reactive.value(None)
    trigger_response = reactive.value(None)
    prompt_body_state_auto = reactive.value([{"role": "System",
                                              "content": "Please give the counter example words in English, Dutch, Russian, French and Dutch"}])
    steps_state = reactive.value(10)
    confirmed_implications = reactive.value([])
    skipped_implications = reactive.value([])
    implication_generator = reactive.value(None)

    @output
    @render.ui
    def render_starting_ui_auto_mode():
        context = cxt.get()
        if context is None:
            return ui.div(
                ui.strong(f"Action requires an input file.",
                          style="color: red; margin-top: 100px; margin-left: 30px;"),
                style="margin-top: 30px; margin-left: 24px;"
            )
        else:
            return ui.div("")

    @reactive.effect
    def start_implication_generator():
        context = cxt.get()
        if context is not None:
            implication_generator.set(context.Basic_Exploration.relative_basis_generator_for_auto_mode())
        return None

    @output
    @render.ui
    def render_steps_and_prompt_input_button():
        context = cxt.get()
        if context is not None:
            return ui.layout_columns(
                ui.input_text_area("system_prompt", "System Prompt",
                                   "You're a logical and deep reasoner, please give the counter example words in English, Dutch, Russian, French and Dutch"),
                ui.input_numeric("steps", "Implications to process before stopping", 10, min=1, max=3000),
            )
        else:
            return ui.div("")

    @reactive.effect
    @reactive.event(input.system_prompt)
    def handle_system_prompt_input():
        if input.system_prompt() is not None:
            prompt = [{"role": "System", "content": input.system_prompt()}]
            prompt_body_state_auto.set(prompt)

    @reactive.effect
    @reactive.event(input.steps)
    def handle_number_of_steps_input():
        if steps_state.get() is not None:
            steps_state.set(input.steps())

    @output
    @render.ui
    def render_start_exploration_button_auto_mode():
        context = cxt.get()
        if context is not None:
            return ui.div(
                ui.input_action_button("start_exploration", "Start Exploration", class_="btn-success",
                                       style="margin-top: 10px;width: 250px;", ),
                ui.strong("❗️❗❗️This process starts from the first implication by default",
                          style="font-size: 12px;color:red; margin-top: 10px;"),
                ui.p("^ Please press the button only once",
                     style="font-size: 12px; margin-top: 10px; margin-bottom: 0px;"),
                ui.p("^ The process will only end once the exploration is complete",
                     style="font-size: 12px;margin-bottom: 0px;"),
                style="display: flex; flex-direction: column; align-items: center; margin-top: 50px;",
            )
        else:
            return ui.div("")

    @reactive.effect
    @reactive.event(input.start_exploration)
    def handle_start_exploration_button_auto_mode():
        if input.start_exploration():
            trigger_response.set("Start")

    def get_model_response(premise, conclusion, context):
        n = 3  # number of tries
        print("\n-----------------------------")

        if context is not None:
            for i in range(n):
                imp = " , ".join(premise) + " => " + " , ".join(conclusion)
                print("Try : ", i + 1, " For : ", imp)

                _, _, _, examples = context_data()
                attr = context.Basic_Exploration.get_current_attributes()
                objects = context.Basic_Exploration.get_current_objects()

                prompt = set_prompt(
                    objects=objects,
                    frames=attr,
                    examples=examples,
                    premise=premise,
                    conclusion=conclusion
                )

                set_prompts = prompt_body_state_auto.get()

                if set_prompts[-1]["role"] != "user":
                    set_prompts.append({"role": "user", "content": prompt})

                result_str = evaluate_prompt_auto(set_prompts)
                set_prompts.append({"role": "assistant", "content": result_str})

                try:
                    result = json.loads(result_str)

                except json.decoder.JSONDecodeError:
                    print("Json decoder error")
                    set_prompts.append(
                        {"role": "user",
                         "content": f"Please respond again with only a valid JSON object. Do not include markdown syntax (like triple backticks) or any explanatory text."})
                    prompt_body_state_auto.set(set_prompts)
                    continue

                if result["output"] == "NO" and result["verb"] in objects:
                    print("Verb already present error")
                    set_prompts.append(
                        {"role": "user",
                         "content": f"Verb '{result["verb"]}' already present in the context, please use another counterexample, or confirm the hypothesis."})
                    prompt_body_state_auto.set(set_prompts)
                    continue

                if result["output"] == "NO":
                    try:
                        print("Implication rejected, with CE verb : ", result['verb'], "with associated meanings : ",
                              result['meaning'])
                        context.Basic_Exploration.check_counter_example_for_attr_auto_mode(result["meaning"], premise,
                                                                                             conclusion,
                                                                                             context.Basic_Exploration.confirmed_attribute_implications)

                        print("Counter Example is Valid, setting the result")
                        trigger_recalc.set(trigger_recalc.get() + 1)
                        prompt_body_state_auto.set([{"role": "System", "content": input.system_prompt()}])
                        return result

                    except Exception as e:
                        print("Invalid Counter example", e)
                        set_prompts.append(
                            {"role": "user",
                             "content": f"The counter example that you provided is invalid because {e}"})
                        prompt_body_state_auto.set(set_prompts)
                        pass

                elif result["output"] == "YES":
                    print("Implication Accepted, setting the result")
                    trigger_recalc.set(trigger_recalc.get() + 1)
                    prompt_body_state_auto.set([{"role": "System", "content": input.system_prompt()}])
                    return result

            print(f"Maximum({i + 1}) tries reached, implication is skipped")
            response_content = json.dumps({"output": "SKIP"})
            result = json.loads(response_content)
            return result

        else:
            return None

    def set_result(result, premise, conclusion, context):
        if result["output"] == "NO":
            context.Basic_Exploration.set_counter_example_auto(result["verb"], result["meaning"])
            trigger_recalc.set(trigger_recalc.get() + 1)
            imp = ",".join(premise) + " => " + ",".join(conclusion)
            
            return "Rejected", set(result["meaning"]), ui.card(
                ui.div(
                    ui.strong(
                        f'For implication : {imp}'),
                    ui.HTML(
                        f"<div>Model suggested that the implication is invalid and</div>"),
                    ui.HTML(
                        f"<div>Suggested verb: <strong>{result['verb']}</strong></div>"),
                    ui.HTML(
                        f"<div>With meanings: <strong>{', '.join(result['meaning'])}</strong></div>"),
                )
            )

        elif result["output"] == "YES":
            trigger_recalc.set(trigger_recalc.get() + 1)
            
            return "Confirmed", "", ui.card(
                ui.strong(f'For implication : {imp}'),
                ui.h6("Model confirmed the implication.",
                      style="color:blue; font-weight:bold;")
            )

        elif result["output"] == "SKIP":
            trigger_recalc.set(trigger_recalc.get() + 1)
            
            return "Skipped", "", ui.card(
                ui.strong(f'For implication : {imp}'),
                ui.h6("Model Skipped the implication.",
                      style="color:blue; font-weight:bold;")
            )
        else:
            return None

    @reactive.effect
    def run_exploration():
        if trigger_response.get() == "Start":
            trigger_response.set("stop")
            i = 0

            generator = implication_generator.get()
            context = cxt.get()

            for imp in generator:
                while imp._premise != imp._conclusion:
                    model_response = get_model_response(imp.premise, imp.get_reduced_conclusion(), context)
                    result, counter_intent, set_result_log = set_result(model_response, imp._premise,
                                                                        imp.get_reduced_conclusion(), context)
                    models_response_log_auto.set(ui.div(models_response_log_auto.get(), set_result_log))

                    if result == "Rejected":
                        imp._conclusion &= counter_intent

                    elif result == "Skipped":
                        skipped_implication = skipped_implications.get()
                        skipped_implications.set(skipped_implication.append(imp))
                        break
                    else:
                        context.Basic_Exploration.confirm_attribute_implication_auto_mode(imp)
                        break

                    # no of implications to process before terminating the loop
                    i += 1
                    if i == int(steps_state.get()):
                        print("\nObject check limit reached")
                        # break

            print("----------Exploration Ended----------")

    @output
    @render.ui
    def render_exploration_log_auto_mode():
        model_log = models_response_log_auto.get()
        if model_log is not None:
            return ui.div(
                ui.h6("Exploration completed. The model carried out the following operations:",
                      style="text-align: center; color:green; font-weight:bold; margin-top: 20px;"),
                model_log
            )
        else:
            return ui.div("")