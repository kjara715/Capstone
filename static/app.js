//logic to hide or show recipe details by clicking View Recipe Button
$(document).ready(function() {

    $(".card-text").hide();
    $(".comment-form").hide();
    $("#instructions-list").hide();

    $(document).on("click", ".recipe", function(){

        //change button name depending on if recipe is showing or hidden (starts hidden)
        if($(this).text() === "View Recipe"){
            $(this).text("Hide Recipe")
        } else {
            $(this).text("View Recipe")
        }
        
        //show and hide recipe on each button click
        $(this).parent().parent().parent().children('.card-text').toggle()
        
    });

    $(document).on("click", ".comment", function(){

        $(this).parent().parent().parent().children(".comment-form").toggle()

    });

    $(document).on("click", "#instructions", function(){

        if($(this).text() === "Instructions For New Users"){
            $(this).text("Hide Instructions")
        } else {
            $(this).text("Instructions For New Users")
        }
        $(this).parent().parent().children("#instructions-list").toggle()
    })

})




