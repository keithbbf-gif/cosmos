<?php
/**
 * SLP WOW — GeneratePress child theme.
 *
 * @package slpwow-gp-child
 */

defined( 'ABSPATH' ) || exit;

function slpwow_enqueue_styles() {
	wp_enqueue_style(
		'generatepress-parent',
		get_template_directory_uri() . '/style.css',
		array(),
		wp_get_theme( 'generatepress' )->get( 'Version' )
	);
	wp_enqueue_style(
		'slpwow-child',
		get_stylesheet_uri(),
		array( 'generatepress-parent' ),
		wp_get_theme()->get( 'Version' )
	);
}
add_action( 'wp_enqueue_scripts', 'slpwow_enqueue_styles', 15 );

function slpwow_setup() {
	add_theme_support( 'title-tag' );
	register_nav_menus(
		array(
			'primary' => __( 'Primary', 'slpwow-gp-child' ),
		)
	);
}
add_action( 'after_setup_theme', 'slpwow_setup' );

/**
 * Professional audience notice (not for patient emergencies).
 */
function slpwow_footer_notice() {
	?>
	<div class="sw-footer-note" role="note">
		<p>
			<?php
			esc_html_e(
				'SLP WOW is a professional education community for speech-language pathologists. It does not provide medical advice or patient care. For clinical emergencies, contact local emergency services.',
				'slpwow-gp-child'
			);
			?>
		</p>
	</div>
	<?php
}
add_action( 'generate_after_footer_content', 'slpwow_footer_notice', 8 );
